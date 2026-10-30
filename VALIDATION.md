# Synchronization validation - 2026-10-30

Imported the current WireBundle working tree from ToolsProject commit `5f3b9ae`
plus its seven pre-existing staged files and the Material test correction.
Those working-tree changes are not represented by that commit alone. The task
did not modify the source staging area; a fresh index snapshot was captured
when the follow-up began with the Material correction already staged.

- Compared 370 tracked plugin files across all nine plugins. The new behavior is
  confined to WireBundle: node obstacle avoidance, bounded extra-bend routing,
  backward spline directions, a viewport-clamped shape toolbar and UI automation.
- Preserved both DataAssetManager transient-fixture test overrides and the
  already-committed WireBundle menu formatting. Kept the flattened
  PerformanceInspector layout. Imported C++ changes were formatted in scope;
  comparison against ToolsProject found no unexpected code differences.
- Isolated UE 5.5 Win64 Development host: final build passed; all 151 tests
  passed (137 without warnings, 14 with warnings; zero failed or skipped).
  Suites: CppTemplateGenerator 4, DataAssetManager 30, OutlinerToolkit 4,
  PerformanceInspector 3, UNotepad 38, ValidatorX 22 and WireBundle 50.
- FPShooterEditor Development and DebugGame builds passed after the final
  Material test correction. All 50 WireBundle tests passed in FPShooter
  (49 without warnings, one with warnings). VS2022 project files regenerated.
- ToolsProjectEditor built before the test correction. Its first WireBundle
  run passed 48/50: the Material movement assertion depended on saved grid
  settings, and one UI scenario captured a Slate invalid-window ensure.
  The test now temporarily guards default movement settings and restores the
  previous value. The Slate ensure did not recur in the two isolated full runs.
  The final canonical ToolsProjectEditor DLL build passed, followed by all 50
  WireBundle tests (49 without warnings, one with warnings). The invalid-window
  ensure did not recur in that canonical rerun either. Project files regenerated
  again after the successful final canonical suite.
- ToolsProject VS2022 project files were regenerated after the isolated final
  tests passed. No user content or generated build products were exported.

Evidence: ToolsProject/Saved/PluginSync-20261030 contains canonical and collection
build/test logs and JSON reports. FPShooter/Reviews/PluginSync-20261030 contains
FPShooter builds, integration results, source hashes and pre-transfer backups.
The readable review is FPShooter/Docs/AI/Reviews/PluginSync-20261030/REPORT.md.
No commits, pushes or parent gitlink updates have been made by this transfer.
This is an applied local review package, not a published submodule revision.

ContentBrowserToolkit and TextureChannelPacker have no dedicated suites.
Rendering automation does not replace manual multi-monitor/DPI usability review.

# Synchronization validation - 2026-10-29

Compared all 365 tracked plugin files against ToolsProject commit `695d4ea`.
The collection now contains nine plugins. Imported the CppTemplateGenerator
menu lifecycle fixes, shared class validation, regression tests and documentation,
and added WireBundle 0.8.0 with its 22 automation tests.

All plugin file contents match that source revision, except for two deliberately
preserved DataAssetManager test files from Tools-Plugins commit `486d770`:
`DataAssetManagerTestTypes.h` and `DataAssetManagerWidgetTest.cpp`. These create
and select a transient fixture so tests work without pre-existing project assets.
PerformanceInspector retains the flattened repository layout.

- Built all nine plugins from this working tree using a new minimal UE 5.5 host
  with AdditionalPluginDirectories, Win64 Development, MSVC 14.44: passed,
  248 build actions. The host contains no ToolsProject source or content.
- Automation: 123 tests; 109 succeeded without warnings, 14 succeeded with
  warnings, zero failures and zero skipped tests.
- Suites: CppTemplateGenerator 4, DataAssetManager 30, OutlinerToolkit 4,
  PerformanceInspector 3, UNotepad 38, ValidatorX 22, WireBundle 22.
- Initial NullRHI run aborted inside Unreal's GenericWindow API when a
  WireBundle material test closed an asset editor. Re-ran the complete suite
  using UnrealEditor with the normal renderer and RenderOffscreen: exit code 0.
- DDC-ForceMemoryCache was used for the isolated host. Warnings remain in
  DataAssetManager, ValidatorX null-input tests and two WireBundle material tests.
- Regenerated ToolsProject Visual Studio 2022 project files successfully after
  the tests, following the canonical WireBundle workflow.
- `git diff --check` passed. No generated binaries, caches or test assets are
  included in the source synchronization. No commit or push was performed.

Local evidence is under ToolsProject/Saved/PluginSync: Build.log,
Tests.log (initial NullRHI attempt), TestsRendered.log and ReportRendered/index.json.
This verifies compilation and automation, not manual mouse interaction, GPU
capture accuracy or compatibility with other engine versions/platforms.
ContentBrowserToolkit and TextureChannelPacker still have no dedicated suites.

## Original extraction validation - 2026-10-20

Validated using a separate minimal C++ Unreal Engine 5.5 project on Windows,
with all eight plugins enabled and this repository added from GitHub as
`Plugins/ToolsPlugins` using `git submodule add`.

- Editor target: Win64 Development, UE 5.5 include order, MSVC 14.44.
- Full build from an empty host build directory: passed (63 actions).
- No Tools Project source modules or content were included in the host.
- Automation: 99 tests across the six available plugin test suites.
- The first run passed 98 tests and revealed one test relying on pre-existing
  Data Asset selection. The test now creates and selects its own transient asset.
- After rebuilding that change, all 30 DataAssetManager tests passed (19 without
  warnings, 11 with warnings). The other 69 tests passed in the initial run.
- Tests ran unattended with NullRHI; visual interaction and GPU captures were
  not manually verified.

Non-blocking warnings include the engine's preferred MSVC version notice,
DataAssetManager's deprecated `SDockTab::FArguments::Icon` usage, and warnings
from invalid-input / temporary-asset test scenarios.

ContentBrowserToolkit and TextureChannelPacker were built and loaded but have
no dedicated automation suites. No claim of compatibility with other Unreal
Engine versions or platforms is made.
