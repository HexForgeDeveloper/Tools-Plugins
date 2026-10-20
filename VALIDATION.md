# Extraction validation — 2026-10-20

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
