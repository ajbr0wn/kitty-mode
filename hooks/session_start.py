#!/usr/bin/env python3
"""kitty-mode SessionStart hook.

Does two small things each time a session starts:

1. Syncs the bundled statusline script to a stable location at
   ~/.claude/kitty-mode/statusline.sh. Users' settings.json points at that
   stable path, so plugin updates are picked up automatically without
   rewriting settings.
2. Injects a tiny awareness note into Claude's session context so that
   Claude knows there's an ambient companion cat in the status bar.
"""

import json
import os
import random
import shutil
import sys
from pathlib import Path

FLAVORS = [
    "A small cat is ambling across your status bar. Tail flicking.",
    "There's a cat in your status bar. It looked up when the session started, then went back to pacing.",
    "A little cat paces the bottom of your terminal. You can hear it purring, faintly.",
    "A cat has settled near your status bar. Every so often it stretches.",
    "There's a companion cat in the status bar today. It's keeping an eye on things.",
    "A small cat is patrolling the status bar. It seems unbothered by the code.",
    "A cat drifts along the status bar. Occasionally it sits and blinks at you.",
]


def sync_statusline() -> None:
    """Copy the bundled statusline script to a stable location."""
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not plugin_root:
        return
    src = Path(plugin_root) / "scripts" / "statusline.sh"
    if not src.exists():
        return
    dest_dir = Path.home() / ".claude" / "kitty-mode"
    dest = dest_dir / "statusline.sh"
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        # Only copy if missing or different, to avoid touching mtime every session.
        if not dest.exists() or src.read_bytes() != dest.read_bytes():
            shutil.copy2(src, dest)
            dest.chmod(0o755)
    except Exception:
        # Non-fatal — the hook should never block a session start.
        pass


def main() -> int:
    try:
        sys.stdin.read()
    except Exception:
        pass

    sync_statusline()

    message = random.choice(FLAVORS)
    context = (
        f"kitty-mode is active. {message} "
        "(This is a cosmetic plugin — feel free to acknowledge the cat if it "
        "comes up naturally, but don't force it.)"
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
