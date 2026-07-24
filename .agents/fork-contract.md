# ArmaanBar Fork Contract

This file records intentional differences from upstream. Do not remove, weaken, or take an
upstream change affecting an item below without the fork owner's explicit approval.

Each item must include `Paths`, a behavior to preserve, and a focused verification reference.
Add an item in the same commit as every new intentional fork-specific behavior.

## ArmaanBar product identity

- Paths:
  - `Package.swift`
  - `Scripts/package_app.sh`
  - `Scripts/compile_and_run.sh`
  - `Scripts/sign-and-notarize.sh`
- Preserve: the executable and app bundle are `ArmaanBar`; bundle IDs and signing identifiers use
  `com.armaandave.ArmaanBar`; package scripts never hard-code upstream `CodexBar`.
- Verify: `./Scripts/package_app.sh debug`
- Sync action: ask before accepting any upstream change to these paths.

## Pace wording and presentation

- Paths:
  - `Sources/CodexBar/UsagePaceText.swift`
  - `Sources/CodexBarCore/UsagePace.swift`
  - `Sources/CodexBar/MenuDescriptor.swift`
  - `Sources/CodexBar/MenuCardView+ModelHelpers.swift`
  - `Sources/CodexBar/Resources/`
  - `Tests/CodexBarTests/UsagePaceTextTests.swift`
- Preserve: the fork's Pace wording and user-visible presentation.
- Verify: `Tests/CodexBarTests/UsagePaceTextTests.swift`
- Sync action: ask before accepting any upstream change to these paths.

## Cost-history token cards

- Paths:
  - `Sources/CodexBar/InlineUsageDashboardContent.swift`
  - `Tests/CodexBarTests/InlineCostHistoryDashboardLabelTests.swift`
- Preserve: cost-history cards show `Today tokens` from `sessionTokens`, not `Latest tokens`, and
  show Today tokens before the selected history-window token total such as `30d tokens`.
- Verify: `swift test --filter InlineCostHistoryDashboardLabelTests`
- Sync action: ask before accepting any upstream change to these paths.

## Status-item debug marker

- Paths:
  - `Sources/CodexBar/StatusItemController+Animation.swift`
  - `Tests/CodexBarTests/StatusItemBalanceDisplayTests.swift`
- Preserve: debug builds do not append a visible `D` marker to the menu-bar title.
- Verify: `Tests/CodexBarTests/StatusItemBalanceDisplayTests.swift`
- Sync action: ask before accepting any upstream change to these paths.
