#!/usr/bin/env python3
"""PreToolUse hook: consolidate reflect queues across Conductor workspaces.

Before any claude-reflect skill runs, merges learnings-queue.json items from
all sibling Conductor workspace project folders into the current workspace's
queue, then clears the siblings. /reflect sees the full accumulated queue
regardless of which workspace captured each item.

Race note: read-then-clear is non-atomic. Concurrent reflect invocations across
workspaces (extremely unlikely for a single-user tool) could lose an item
appended between this hook's read and clear. Dedup on (message, timestamp)
prevents double-counting but does not close the window.
"""
import json
import sys
from pathlib import Path
from typing import Optional

_MAX_QUEUE_BYTES = 10 * 1024 * 1024  # 10 MB guard against runaway queues


def _projects_root() -> Path:
    return Path.home() / ".claude" / "projects"


def _current_queue(cwd: Path) -> Path:
    folder = str(cwd).replace("/", "-").replace("\\", "-")
    if not folder.startswith("-"):
        folder = "-" + folder
    return _projects_root() / folder / "learnings-queue.json"


def _conductor_prefix(cwd: Path) -> Optional[str]:
    """Return encoded project-root prefix for a Conductor workspace, or None.

    Conductor paths: .../conductor/workspaces/<project>/<workspace>/
    Prefix encodes .../conductor/workspaces/<project> and is used to match
    sibling workspace folders via startswith, avoiding substring false-positives
    on short project names.
    """
    parts = cwd.parts
    try:
        c_idx = list(parts).index("conductor")
    except ValueError:
        return None
    if c_idx + 3 > len(parts) or parts[c_idx + 1] != "workspaces":
        return None
    project_root = str(Path(*parts[: c_idx + 3])).replace("/", "-").replace("\\", "-")
    if not project_root.startswith("-"):
        project_root = "-" + project_root
    return project_root


def _is_under_projects(path: Path) -> bool:
    try:
        return _projects_root().resolve() in path.resolve().parents
    except OSError:
        return False


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if not isinstance(payload, dict):
        sys.exit(0)

    if payload.get("tool_name") != "Skill":
        sys.exit(0)

    tool_input = payload.get("tool_input", {}) or {}
    if "reflect" not in str(tool_input.get("skill", "")).lower():
        sys.exit(0)

    cwd = Path.cwd()
    prefix = _conductor_prefix(cwd)
    if not prefix:
        sys.exit(0)

    projects_dir = _projects_root()
    if not projects_dir.is_dir():
        sys.exit(0)

    current_queue = _current_queue(cwd)

    all_items = []
    if current_queue.exists():
        try:
            data = json.loads(current_queue.read_text(encoding="utf-8"))
            if isinstance(data, list):
                all_items = data
        except (json.JSONDecodeError, OSError):
            pass

    sibling_dirs = [
        d for d in projects_dir.iterdir()
        if d.is_dir()
        and d.name.startswith(prefix + "-")
        and d != current_queue.parent
    ]

    sibling_queues_to_clear = []
    for sibling in sibling_dirs:
        sibling_queue = sibling / "learnings-queue.json"
        if not sibling_queue.exists() or sibling_queue.is_symlink():
            continue
        if not _is_under_projects(sibling_queue):
            continue
        try:
            if sibling_queue.stat().st_size > _MAX_QUEUE_BYTES:
                continue
        except OSError:
            continue
        try:
            data = json.loads(sibling_queue.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, list):
            continue
        all_items.extend(data)
        sibling_queues_to_clear.append(sibling_queue)

    if not sibling_queues_to_clear:
        sys.exit(0)

    # Deduplicate by (message, timestamp); skip items with empty message
    seen: set = set()
    deduped = []
    for item in all_items:
        if not isinstance(item, dict):
            continue
        msg = item.get("message", "")
        if not msg:
            continue
        key = (msg, item.get("timestamp", ""))
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    if not _is_under_projects(current_queue):
        sys.exit(0)

    try:
        current_queue.parent.mkdir(parents=True, exist_ok=True)
        current_queue.write_text(json.dumps(deduped, indent=2), encoding="utf-8")
    except OSError:
        sys.exit(0)

    for sibling_queue in sibling_queues_to_clear:
        try:
            sibling_queue.write_text("[]", encoding="utf-8")
        except OSError:
            pass

    sys.exit(0)


if __name__ == "__main__":
    main()
