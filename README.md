# Tools Plugins

Reusable Unreal Engine 5.5 plugins maintained by HexForgeDeveloper. Extracted from
[Tools Project](https://github.com/HexForgeDeveloper/Tools-Project), including the
current UNotepad Verse editing support. This repository contains source code;
Unreal builds the modules for the consuming project.

## Included plugins

| Plugin | Purpose |
| --- | --- |
| ContentBrowserToolkit | Asset filters and dependency audits in Content Browser |
| CppTemplateGenerator | Configurable C++ class creation templates |
| DataAssetManager | Browse, edit, compare and validate Data Assets |
| OutlinerToolkit | Actor columns, batch actions and level audits |
| PerformanceInspector | Runtime performance captures and editor reports |
| TextureChannelPacker | Pack, repack and unpack texture channels |
| UNotepad | In-editor text, C++, Verse, JSON and CSV editing |
| ValidatorX | Blueprint and material validation rules |

See [PLUGIN_GUIDE.md](PLUGIN_GUIDE.md) for entry points, settings and workflows.
Most modules are editor-only. PerformanceInspector also has a runtime module.
Verse support is text editing and lexical highlighting, without a Verse compiler
or language server integration.

## Add to an Unreal project

From the root of a Git-tracked Unreal project:

```sh
git submodule add https://github.com/HexForgeDeveloper/Tools-Plugins.git Plugins/ToolsPlugins
git add .gitmodules Plugins/ToolsPlugins
git commit -m "Add Tools Plugins submodule"
```

Unreal discovers the individual `.uplugin` files below `Plugins/ToolsPlugins`.
Enable the desired plugins in Edit > Plugins, regenerate project files where
needed, and build the project's Editor target. Requires Unreal Engine 5.5 and a
compatible C++ toolchain. Other engine versions have not been verified.

Do not keep another copy of the same plugin installed in the project or engine:
duplicate plugin/module names can prevent discovery or compilation.

## Clone a consuming project

```sh
git clone --recurse-submodules <project-url>
```

For an existing checkout:

```sh
git submodule update --init --recursive
```

## Update plugins deliberately

The parent project pins a specific commit, so other developers get the same
plugin version. From the parent project root:

```sh
git -C Plugins/ToolsPlugins fetch origin
git -C Plugins/ToolsPlugins checkout origin/main
git add Plugins/ToolsPlugins
git commit -m "Update Tools Plugins"
```

Build and test the consuming project before committing an updated pointer.

## Contribute changes from a submodule

Submodules commonly start with a detached HEAD. Create a branch inside the
submodule before editing, commit and push there first, then commit the updated
submodule pointer in the parent repository:

```sh
git -C Plugins/ToolsPlugins switch -c my-plugin-change
# Edit, build and test.
git -C Plugins/ToolsPlugins add <changed-files>
git -C Plugins/ToolsPlugins commit -m "Describe the plugin change"
git -C Plugins/ToolsPlugins push -u origin my-plugin-change
git add Plugins/ToolsPlugins
git commit -m "Update plugin revision"
```

The submodule downloads this entire collection. Enable only the plugins needed
in each project. Git cannot use a subdirectory as an independent submodule; for
independent downloads/versioning, each plugin would need its own repository.

Tools Project's existing plugin copies do not automatically synchronize with
this repository. Future shared changes should be made here; replacing those
copies with a submodule is a separate migration.

## Tests

In the Unreal Editor Session Frontend automation window, use these test filters:
`CppTemplateGenerator`, `DataAssetManager`, `OutlinerToolkit`,
`PerformanceInspector`, `UNotepad`, `ValidatorX`.

ContentBrowserToolkit and TextureChannelPacker currently have no dedicated
automation test modules. Tests should run in a disposable test project because
some create temporary assets.

## License

[MIT](LICENSE). Existing copyright notices are preserved.
