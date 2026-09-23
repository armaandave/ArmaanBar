# Fork Contract

This file records intentional differences from upstream. Do not remove, weaken, or take an
upstream change affecting an item below without the fork owner's explicit approval.

Each item must include `Paths`, a behavior to preserve, and a focused verification reference.
Add an item in the same commit as every new intentional fork-specific behavior.

## Menu bar period display

- Paths:
  - `Sources/CodexBar/MenuBarDisplayText.swift`
  - `Sources/CodexBar/StatusItemController+Animation.swift`
  - `Sources/CodexBar/UsageStore+HistoricalPace.swift`
  - `Tests/CodexBarTests/StatusItemAnimationTests.swift`
  - `Tests/CodexBarTests/ProviderArchitectureGatekeeperTests.swift`
- Preserve: `both` mode shows quota percent and elapsed or remaining period percent as `quota% @ period%`.
  It keeps period progress near a reset and when the quota is exhausted.
- Verify: `Tests/CodexBarTests/StatusItemAnimationTests.swift`
- Sync action: ask before accepting any upstream change to these paths.
