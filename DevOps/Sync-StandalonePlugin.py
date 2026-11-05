#!/usr/bin/env python3
"""@brief Export tracked plugin payloads without overwriting standalone repository metadata."""
import argparse
from pathlib import Path, PurePosixPath
import shutil
import subprocess

PLUGINS = ("CppTemplateGenerator", "TextureChannelPacker")
DIRECTORIES = ("Source", "Config", "Content", "Resources", "Shaders")
EXCLUDED_DIRS = {".git", ".agents", ".codex", ".claude", "Binaries", "Intermediate", "Saved", "DerivedDataCache"}
EXCLUDED_FILES = {"AGENTS.md", "CLAUDE.md", "GEMINI.md", "ROADMAP.md", "RELEASE_PLAN.md", "REALEASE_PLAN.md", "COMMIT_MESSAGE.md"}
CONTROL_PATHS = (".github/workflows/sync-standalone-plugins.yml", "DevOps/Sync-StandalonePlugin.py", "DevOps/Tests/test_sync_standalone_plugin.py")


def git(root, *arguments):
    """@brief Run Git without a shell and return decoded stdout; failures stop synchronization."""
    return subprocess.check_output(["git", "-C", str(root), *arguments], text=True, encoding="utf-8").strip()


def excluded(relative):
    """@brief Identify generated files and local assistant materials that never belong to the payload."""
    return any(part in EXCLUDED_DIRS for part in relative.parts) or relative.name in EXCLUDED_FILES


def validate_plugin(plugin):
    """@brief Reject names outside the explicit release allowlist."""
    if plugin not in PLUGINS:
        raise ValueError(f"Unsupported plugin: {plugin}")


def changed(root, plugin, event, before, after, requested="all"):
    """@brief Select only the affected plugin, or the requested plugin during manual dispatch."""
    validate_plugin(plugin)
    if event == "workflow_dispatch":
        return requested in ("all", plugin)
    if not before or set(before) == {"0"}:
        return True
    paths = git(root, "diff", "--name-only", before, after, "--", f"{plugin}/", *CONTROL_PATHS)
    return bool(paths)


def ensure_checkout(root):
    """@brief Require the destination itself to be a Git worktree root, not an arbitrary subdirectory."""
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("Destination must be the Git worktree root")


def safe_path(root, relative):
    """@brief Reject symlinks and paths escaping a managed worktree before accessing their contents."""
    path = root
    for index, part in enumerate(relative.parts):
        if part in ("", ".", ".."):
            raise ValueError(f"Unsafe path: {relative}")
        path = path / part
        if index < len(relative.parts) - 1 and path.exists() and not path.is_dir():
            raise ValueError(f"Parent path is blocked by a file: {path}")
        if path.is_symlink():
            raise ValueError(f"Symlink is not supported: {path}")
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"Path escapes worktree: {relative}")
    return path


def sync(root, destination, plugin):
    """@brief Mirror tracked payload files; preserve root README and standalone repository metadata.

    Only managed payload directories and the descriptor/LICENSE are changed. Deletions
    propagate inside those directories. Ignored local data is preserved. All paths are
    validated before the first mutation; Git records the resulting content changes.
    """
    validate_plugin(plugin)
    root, destination = root.resolve(), destination.resolve()
    ensure_checkout(destination)
    if root == destination or root.is_relative_to(destination) or destination.is_relative_to(root):
        raise ValueError("Source and destination worktrees must be separate")
    source = safe_path(root, PurePosixPath(plugin))
    tracked = git(root, "ls-files", "-z", "--", f"{plugin}/").split("\0")
    payload = {}
    for filename in filter(None, tracked):
        relative = PurePosixPath(filename).relative_to(plugin)
        if excluded(relative):
            continue
        if relative.parts[0] not in DIRECTORIES and str(relative) not in (f"{plugin}.uplugin", "LICENSE"):
            continue
        origin = safe_path(source, relative)
        if not origin.is_file():
            raise ValueError(f"Tracked source is not a regular file: {origin}")
        safe_path(destination, relative)
        payload[relative] = origin
    if PurePosixPath(f"{plugin}.uplugin") not in payload or not any(p.parts[0] == "Source" for p in payload):
        raise ValueError("Plugin descriptor and tracked Source files are required")
    stale = []
    for directory in DIRECTORIES:
        path = safe_path(destination, PurePosixPath(directory))
        if not path.exists():
            continue
        if not path.is_dir():
            raise ValueError(f"Managed directory is blocked by a file: {path}")
        for entry in path.rglob("*"):
            relative = PurePosixPath(entry.relative_to(destination).as_posix())
            if excluded(relative):
                continue
            safe_path(destination, relative)
            if entry.is_file() and relative not in payload:
                stale.append(entry)
    for relative, origin in payload.items():
        target = safe_path(destination, relative)
        if target.exists() and not target.is_file():
            raise ValueError(f"Managed file is blocked by a directory: {target}")
    for entry in stale:
        entry.unlink()
    copied = 0
    for relative, origin in payload.items():
        target = safe_path(destination, relative)
        if target.is_file() and target.read_bytes() == origin.read_bytes():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origin, target)
        copied += 1
    print(f"{plugin}: {copied} files updated, {len(stale)} stale files removed")


def main():
    """@brief Parse trusted workflow arguments and run selection or payload synchronization."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("changed", "sync"))
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--plugin", choices=PLUGINS, required=True)
    parser.add_argument("--destination-root", type=Path)
    parser.add_argument("--event", default="push")
    parser.add_argument("--before", default="")
    parser.add_argument("--after", default="HEAD")
    parser.add_argument("--requested-plugin", choices=("all", *PLUGINS), default="all")
    args = parser.parse_args()
    if args.command == "changed":
        selected = changed(args.source_root, args.plugin, args.event, args.before, args.after, args.requested_plugin)
        print(f"changed={str(selected).lower()}")
    else:
        if args.destination_root is None:
            parser.error("sync requires --destination-root")
        sync(args.source_root, args.destination_root, args.plugin)


if __name__ == "__main__":
    main()
