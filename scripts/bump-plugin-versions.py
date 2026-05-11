#!/usr/bin/env python3
"""
Bump plugin versions based on what changed vs origin/BASE.

Structural changes (new/removed skills, commands, or hook scripts) -> minor bump.
Content-only changes -> patch bump.

Usage:
    python3 scripts/bump-plugin-versions.py [--base <ref>]

Defaults to comparing against origin/main. Pass --base to override.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys


def run(cmd):
    return subprocess.check_output(cmd, text=True).strip()


def ls_tree(ref, path):
    try:
        out = run(["git", "ls-tree", "--name-only", ref, path])
        return set(out.splitlines()) if out else set()
    except subprocess.CalledProcessError:
        return set()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=None, help="Base ref to diff against (default: origin/<HEAD branch>)")
    args = parser.parse_args()

    if args.base:
        base_ref = args.base
    else:
        try:
            env = {**os.environ, "LC_ALL": "C"}
            head_branch = subprocess.check_output(
                ["git", "remote", "show", "origin"], text=True, env=env
            ).strip().splitlines()
            head_branch = next(l.split()[-1] for l in head_branch if "HEAD branch" in l)
        except (StopIteration, subprocess.CalledProcessError):
            head_branch = "main"
        base_ref = f"origin/{head_branch}"

    try:
        changed = run(["git", "diff", f"{base_ref}...HEAD", "--name-only"]).splitlines()
    except subprocess.CalledProcessError as e:
        print(f"git diff failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not changed:
        print("No changes vs base. Nothing to bump.")
        return

    bumped = []
    bumped_paths = []

    for plugin_json_path in sorted(glob.glob("plugins/*/.claude-plugin/plugin.json")):
        plugin_dir = os.path.dirname(os.path.dirname(plugin_json_path))
        prefix = plugin_dir + "/"

        content_changes = [
            f for f in changed
            if f.startswith(prefix) and f != plugin_json_path
        ]
        if not content_changes:
            continue

        if plugin_json_path in changed:
            print(f"Skipping {plugin_json_path}: already modified in this branch.")
            continue

        structural = (
            ls_tree(base_ref, prefix + "skills/") != ls_tree("HEAD", prefix + "skills/") or
            ls_tree(base_ref, prefix + "commands/") != ls_tree("HEAD", prefix + "commands/") or
            {f for f in ls_tree(base_ref, prefix + "hooks/") if f.endswith(".sh")} !=
            {f for f in ls_tree("HEAD", prefix + "hooks/") if f.endswith(".sh")}
        )

        with open(plugin_json_path, encoding="utf-8") as f:
            data = json.load(f)

        version = data.get("version", "")
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            print(f"Skipping {plugin_json_path}: invalid version {version!r}", file=sys.stderr)
            continue

        parts = version.split(".")
        bump_type = "minor" if structural else "patch"
        if structural:
            parts[1] = str(int(parts[1]) + 1)
            parts[2] = "0"
        else:
            parts[2] = str(int(parts[2]) + 1)
        new_version = ".".join(parts)
        data["version"] = new_version

        tmp = plugin_json_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp, plugin_json_path)

        bumped_paths.append(plugin_json_path)
        bumped.append(f"{data['name']} {version} -> {new_version} ({bump_type})")
        print(f"Bumped: {bumped[-1]}")

    if bumped:
        summary = "; ".join(b.rsplit(" (", 1)[0] for b in bumped)
        # --only commits exactly these paths from the working tree, leaving
        # any other staged changes in the caller's index untouched.
        subprocess.run(
            ["git", "commit", "--only", "-m", f"chore: bump plugin versions ({summary})", "--"] + bumped_paths,
            check=True,
        )
        print(f"\nCommitted: {summary}")
    else:
        print("No plugin version changes needed.")


if __name__ == "__main__":
    main()
