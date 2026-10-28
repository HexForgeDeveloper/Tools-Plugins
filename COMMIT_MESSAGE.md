feat(plugins): sync ToolsProject updates and add WireBundle

Bring the plugin collection up to date with ToolsProject commit 695d4ea.

- Import CppTemplateGenerator menu ownership and cleanup fixes, shared parent
  class validation, regression tests, README and packaging filter.
- Add WireBundle 0.8.0, including native reroute bundling, persistent registration,
  unbundling, alignment, chain collapse and selection-isolated shape editing.
- Include WireBundle's separate automation module and 22 regression tests.
- Preserve the DataAssetManager fixture fix for projects without existing assets.
- Update the collection README, plugin guide and validation record.

Validation: all nine plugins built in an isolated UE 5.5 Win64 Development host.
All 123 automation tests passed with the normal renderer and RenderOffscreen
(109 without warnings, 14 with warnings). The initial NullRHI run aborted in
Unreal's window API during a material-editor test; the complete rendered rerun
passed. Regenerated ToolsProject VS2022 project files; git diff --check passed.
