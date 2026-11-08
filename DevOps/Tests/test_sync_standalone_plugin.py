"""@brief Regression tests for scoped exports, deletions, change detection and idempotence."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("sync_plugin", Path(__file__).parents[1] / "Sync-StandalonePlugin.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SyncTests(unittest.TestCase):
    """@brief Exercise real Git worktrees while keeping all generated fixtures in a temporary directory."""

    def setUp(self):
        """@brief Create independent source and destination repositories with one tracked plugin."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.target = self.root / "target"
        for path in (self.source, self.target):
            path.mkdir()
            self.command(path, "init", "-q")
            self.command(path, "config", "user.name", "Sync Test")
            self.command(path, "config", "user.email", "sync-test@example.invalid")
        self.write(self.source, "CppTemplateGenerator/CppTemplateGenerator.uplugin", "{}")
        self.write(self.source, "CppTemplateGenerator/Source/Test.cpp", "source")
        self.write(self.source, "CppTemplateGenerator/LICENSE", "license")
        self.write(self.source, "CppTemplateGenerator/README.md", "collection readme")
        self.commit(self.source)
        self.before = MODULE.git(self.source, "rev-parse", "HEAD")
        self.write(self.target, "README.md", "standalone readme")
        self.write(self.target, ".github/workflows/custom.yml", "custom workflow")
        self.commit(self.target)

    def command(self, root, *args):
        """@brief Run checked fixture Git commands without exposing command output on success."""
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

    def write(self, root, relative, text):
        """@brief Write a test-owned fixture file, creating its parent directories."""
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def commit(self, root):
        """@brief Record fixture content so the export sees only committed/tracked files."""
        self.command(root, "add", ".")
        self.command(root, "commit", "-qm", "fixture")

    def test_export_preserves_repository_metadata(self):
        """@brief Mirror payloads without replacing standalone documentation or workflow files."""
        MODULE.sync(self.source, self.target, "CppTemplateGenerator")
        self.assertEqual((self.target / "Source/Test.cpp").read_text(), "source")
        self.assertEqual((self.target / "README.md").read_text(), "standalone readme")
        self.assertEqual((self.target / ".github/workflows/custom.yml").read_text(), "custom workflow")
        self.assertEqual((self.target / "LICENSE").read_text(), "license")

    def test_deletes_only_stale_managed_files(self):
        """@brief Remove stale source while preserving unrelated root files and excluded local data."""
        self.write(self.target, "Source/Stale.cpp", "stale")
        self.write(self.target, "Source/Saved/local.txt", "local")
        self.write(self.target, "unmanaged.txt", "unmanaged")
        MODULE.sync(self.source, self.target, "CppTemplateGenerator")
        self.assertFalse((self.target / "Source/Stale.cpp").exists())
        self.assertTrue((self.target / "Source/Saved/local.txt").exists())
        self.assertTrue((self.target / "unmanaged.txt").exists())

    def test_excludes_generated_and_local_materials(self):
        """@brief Even tracked generated/assistant files are excluded; untracked files never export."""
        self.write(self.source, "CppTemplateGenerator/Source/AGENTS.md", "local")
        self.write(self.source, "CppTemplateGenerator/Source/Binaries/output.dll", "binary")
        self.commit(self.source)
        self.write(self.source, "CppTemplateGenerator/Source/Untracked.cpp", "untracked")
        MODULE.sync(self.source, self.target, "CppTemplateGenerator")
        for relative in ("Source/AGENTS.md", "Source/Binaries/output.dll", "Source/Untracked.cpp"):
            self.assertFalse((self.target / relative).exists())

    def test_repeat_export_is_a_git_noop(self):
        """@brief A repeated synchronization produces no new Git changes or required commit."""
        MODULE.sync(self.source, self.target, "CppTemplateGenerator")
        self.commit(self.target)
        MODULE.sync(self.source, self.target, "CppTemplateGenerator")
        self.assertEqual(MODULE.git(self.target, "status", "--porcelain"), "")

    def test_missing_descriptor_does_not_delete_destination(self):
        """@brief Validate the entire payload before deleting stale destination files."""
        self.command(self.source, "rm", "CppTemplateGenerator/CppTemplateGenerator.uplugin")
        sentinel = self.write(self.target, "Source/Keep.cpp", "keep")
        with self.assertRaises(ValueError):
            MODULE.sync(self.source, self.target, "CppTemplateGenerator")
        self.assertEqual(sentinel.read_text(), "keep")

    def test_directory_blocker_does_not_delete_destination(self):
        """@brief Reject a file blocking a managed directory before touching destination content."""
        sentinel = self.write(self.target, "Source", "keep")
        with self.assertRaises(ValueError):
            MODULE.sync(self.source, self.target, "CppTemplateGenerator")
        self.assertEqual(sentinel.read_text(), "keep")

    def test_unrelated_plugin_does_not_select_destination(self):
        """@brief Editing one plugin must not trigger a commit in the other repository."""
        self.write(self.source, "TextureChannelPacker/Source/Other.cpp", "other")
        self.commit(self.source)
        after = MODULE.git(self.source, "rev-parse", "HEAD")
        self.assertFalse(MODULE.changed(self.source, "CppTemplateGenerator", "push", self.before, after))
        self.assertTrue(MODULE.changed(self.source, "TextureChannelPacker", "push", self.before, after))

    def test_nonplugin_change_does_not_select_either_destination(self):
        """@brief Collection-only documentation changes require no standalone update."""
        self.write(self.source, "README.md", "collection only")
        self.commit(self.source)
        after = MODULE.git(self.source, "rev-parse", "HEAD")
        for plugin in MODULE.PLUGINS:
            self.assertFalse(MODULE.changed(self.source, plugin, "push", self.before, after))

    def test_workflow_change_selects_both_for_revalidation(self):
        """@brief A sync implementation change rechecks both targets, still allowing a content no-op."""
        self.write(self.source, MODULE.CONTROL_PATHS[0], "workflow")
        self.commit(self.source)
        after = MODULE.git(self.source, "rev-parse", "HEAD")
        for plugin in MODULE.PLUGINS:
            self.assertTrue(MODULE.changed(self.source, plugin, "push", self.before, after))

    def test_manual_selection_is_scoped(self):
        """@brief Manual dispatch can update one plugin without selecting the other."""
        for plugin in MODULE.PLUGINS:
            self.assertEqual(MODULE.changed(self.source, plugin, "workflow_dispatch", "", "HEAD", "CppTemplateGenerator"), plugin == "CppTemplateGenerator")

    def test_data_asset_manager_exports_release_without_tests(self):
        """@brief Keep development tests and beta metadata out of the standalone release."""
        plugin = "DataAssetManager"
        descriptor = {
            "IsBetaVersion": True,
            "Modules": [{"Name": plugin}, {"Name": "DataAssetManagerTests"}],
        }
        self.write(self.source, f"{plugin}/{plugin}.uplugin", json.dumps(descriptor))
        self.write(self.source, f"{plugin}/Source/{plugin}/Editor.cpp", "editor")
        self.write(self.source, f"{plugin}/Source/DataAssetManagerTests/Test.cpp", "test")
        self.write(self.target, "Source/DataAssetManagerTests/Stale.cpp", "stale test")
        self.commit(self.source)

        after = MODULE.git(self.source, "rev-parse", "HEAD")
        for candidate in MODULE.PLUGINS:
            self.assertEqual(MODULE.changed(self.source, candidate, "push", self.before, after), candidate == plugin)
        MODULE.sync(self.source, self.target, plugin)
        published = json.loads((self.target / f"{plugin}.uplugin").read_text())
        self.assertFalse(published["IsBetaVersion"])
        self.assertEqual(published["Modules"], [{"Name": plugin}])
        self.assertEqual((self.target / f"Source/{plugin}/Editor.cpp").read_text(), "editor")
        self.assertFalse((self.target / "Source/DataAssetManagerTests/Test.cpp").exists())
        self.assertFalse((self.target / "Source/DataAssetManagerTests/Stale.cpp").exists())
        self.assertEqual((self.target / "README.md").read_text(), "standalone readme")
        self.commit(self.target)
        MODULE.sync(self.source, self.target, plugin)
        self.assertEqual(MODULE.git(self.target, "status", "--porcelain"), "")

    def test_plugin_allowlist_rejects_traversal(self):
        """@brief Plugin arguments cannot become arbitrary filesystem destinations."""
        with self.assertRaises(ValueError):
            MODULE.sync(self.source, self.target, "../target")


if __name__ == "__main__":
    unittest.main()
