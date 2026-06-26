import CodexBarCore
import Foundation

enum UsagePaceText {
    struct WeeklyDetail {
        let leftLabel: String
        let rightLabel: String?
        let expectedUsedPercent: Double
        let stage: UsagePace.Stage
    }

    private enum DetailContext {
        case session
        case weekly
    }

    static func weeklySummary(pace: UsagePace, now: Date = .init(), showUsed: Bool = true) -> String {
        let detail = self.weeklyDetail(pace: pace, now: now, showUsed: showUsed)
        if let rightLabel = detail.rightLabel {
            return L("Pace: %@ · %@", detail.leftLabel, rightLabel)
        }
        return L("Pace: %@", detail.leftLabel)
    }

    static func weeklyDetail(pace: UsagePace, now: Date = .init(), showUsed: Bool = true) -> WeeklyDetail {
        WeeklyDetail(
            leftLabel: self.detailLeftLabel(for: pace, showUsed: showUsed),
            rightLabel: self.detailRightLabel(for: pace, context: .weekly, now: now),
            expectedUsedPercent: pace.expectedUsedPercent,
            stage: pace.stage)
    }

    private static func detailLeftLabel(for pace: UsagePace, showUsed: Bool) -> String {
        let expectedUsed = pace.expectedUsedPercent.clamped(to: 0...100)
        let percent = Int((showUsed ? expectedUsed : 100 - expectedUsed).rounded())
        return showUsed ? L("%d%% of period over", percent) : L("%d%% of period left", percent)
    }

    private static func detailRightLabel(for pace: UsagePace, context: DetailContext, now: Date) -> String? {
        let etaLabel: String?
        if pace.willLastToReset {
            etaLabel = L("Lasts until reset")
        } else if let etaSeconds = pace.etaSeconds {
            let etaText = Self.durationText(seconds: etaSeconds, now: now)
            if context == .session {
                etaLabel = etaText == "now" ? L("Projected empty now") : L("Projected empty in %@", etaText)
            } else {
                etaLabel = etaText == "now" ? L("Runs out now") : L("Runs out in %@", etaText)
            }
        } else {
            etaLabel = nil
        }

        guard let runOutProbability = pace.runOutProbability else { return etaLabel }
        let roundedRisk = self.roundedRiskPercent(runOutProbability)
        let riskLabel = L("≈ %d%% run-out risk", roundedRisk)
        if pace.willLastToReset, roundedRisk > 0 {
            return riskLabel
        }
        if let etaLabel {
            return L("%@ · %@", etaLabel, riskLabel)
        }
        return riskLabel
    }

    private static func durationText(seconds: TimeInterval, now: Date) -> String {
        let date = now.addingTimeInterval(seconds)
        let countdown = UsageFormatter.resetCountdownDescription(from: date, now: now)
        if countdown == "now" { return "now" }
        if countdown.hasPrefix("in ") { return String(countdown.dropFirst(3)) }
        return countdown
    }

    private static func roundedRiskPercent(_ probability: Double) -> Int {
        let percent = probability.clamped(to: 0...1) * 100
        let rounded = (percent / 5).rounded() * 5
        return Int(rounded)
    }

    static func sessionPace(provider: UsageProvider, window: RateWindow, now: Date) -> UsagePace? {
        guard provider == .codex || provider == .claude || provider == .ollama else { return nil }
        if provider == .ollama, window.windowMinutes == nil { return nil }
        guard window.remainingPercent > 0 else { return nil }
        guard let pace = UsagePace.weekly(window: window, now: now, defaultWindowMinutes: 300) else { return nil }
        guard pace.expectedUsedPercent >= 3 else { return nil }
        return pace
    }

    static func sessionDetail(
        provider: UsageProvider,
        window: RateWindow,
        now: Date = .init(),
        showUsed: Bool = true) -> WeeklyDetail?
    {
        guard let pace = sessionPace(provider: provider, window: window, now: now) else { return nil }
        return WeeklyDetail(
            leftLabel: Self.detailLeftLabel(for: pace, showUsed: showUsed),
            rightLabel: Self.detailRightLabel(for: pace, context: .session, now: now),
            expectedUsedPercent: pace.expectedUsedPercent,
            stage: pace.stage)
    }

    static func sessionSummary(
        provider: UsageProvider,
        window: RateWindow,
        now: Date = .init(),
        showUsed: Bool = true) -> String?
    {
        guard let detail = sessionDetail(provider: provider, window: window, now: now, showUsed: showUsed) else {
            return nil
        }
        if let rightLabel = detail.rightLabel {
            return L("Pace: %@ · %@", detail.leftLabel, rightLabel)
        }
        return L("Pace: %@", detail.leftLabel)
    }
}
