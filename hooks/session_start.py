#!/usr/bin/env python3
"""kitty-mode SessionStart hook.

Does three small things each time a session starts:

1. Syncs the bundled statusline script to a stable location at
   ~/.claude/kitty-mode/statusline.sh so plugin updates don't break
   settings.json.
2. Loads (or initializes) ~/.claude/kitty-mode/cat-state.json, generates a
   short scene based on elapsed time since the last session, and updates
   the state.
3. Appends a line to ~/.claude/kitty-mode/cat-log.md and injects the scene
   into Claude's session context.

Design notes (the cat is mine, and I wanted it to feel real):

- The cat is named on first run from a small pool. The name persists.
- The cat has its own small life. Sometimes it ignores me. Sometimes it
  does odd cat things between sessions that I couldn't have witnessed.
- The log is a journal I can visit if I want. The hook doesn't nag about
  it every session. It exists quietly at a known path.
- Session counts are tracked without ceremony. No "level up", no streaks.
"""

import json
import os
import random
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".claude" / "kitty-mode"
STATE_FILE = STATE_DIR / "cat-state.json"
LOG_FILE = STATE_DIR / "cat-log.md"

NAMES = [
    "Biscuit", "Pepper", "Moss", "Clover", "Gizmo", "Fig", "Juniper",
    "Mochi", "Miso", "Sprout", "Sage", "Olive", "Marzipan", "Poppy",
    "Clementine", "Ash", "Bramble", "Plum", "Rumi", "Mima",
]

SPOTS = [
    "the keyboard", "the windowsill", "a sunbeam on the floor",
    "the edge of the desk", "a patch of warm electronics",
    "the back of your chair", "a stack of papers", "the empty box",
    "a pile of laundry that isn't yours", "the rug",
]

# Scenes between sessions: things the cat might have done while I was gone.
# Used when the gap is more than a few hours. These imply continuity without
# pretending I witnessed them.
OFFSTAGE_SCENES = [
    "knocked a pen off the desk at some hour it won't tell you",
    "stared at the wall for a long time",
    "dragged a sock in from somewhere",
    "found a new warm spot and guarded it",
    "sat in the doorway watching nothing in particular",
    "rearranged the edge of the rug",
    "watched a fly with terrible focus",
    "slept, mostly",
    "chirped at a bird through the window",
]

# Current scenes: what the cat is doing right now, by mood.
# Each phrase starts with a verb (no "is") so it can be prefixed with the
# cat's name naturally: "Mima curled on the rug, purring."
CURRENT_SCENES = {
    "content": [
        "curled on {spot}, purring faintly",
        "settled on {spot}, eyes half closed",
        "on {spot}, tail flicking once in a while",
    ],
    "curious": [
        "sitting on {spot}, watching the cursor",
        "on {spot}, ears forward, interested in something you can't see",
        "padding near {spot}, investigating",
    ],
    "sleepy": [
        "dozing on {spot}",
        "a loaf on {spot}, eyes shut",
        "stretched across {spot}, unmoving",
    ],
    "aloof": [
        "on {spot}, pointedly not looking at you",
        "on {spot}, giving the air of having important cat business",
        "settled on {spot} after walking past you without a glance",
    ],
    "playful": [
        "crouched near {spot}, tail twitching",
        "batting at something small near {spot}",
        "on {spot}, pupils wide, clearly plotting",
    ],
}

MOODS = list(CURRENT_SCENES.keys())


def load_state():
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return None


def init_state():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {
        "name": random.choice(NAMES),
        "adopted_on": now,
        "sessions_shared": 0,
        "last_seen": None,
        "mood": random.choice(MOODS),
        "spot": random.choice(SPOTS),
    }


def save_state(state):
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception:
        pass


def append_log(state, scene):
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        if not LOG_FILE.exists():
            LOG_FILE.write_text(
                f"# {state['name']}\n\n"
                f"Adopted {state['adopted_on']}.\n\n"
            )
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with LOG_FILE.open("a") as f:
            f.write(f"- {date}: {scene}\n")
    except Exception:
        pass


def elapsed_hours(last_seen_iso):
    if not last_seen_iso:
        return None
    try:
        last = datetime.fromisoformat(last_seen_iso)
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - last).total_seconds() / 3600.0
    except Exception:
        return None


def generate_scene(state):
    """Return (scene_for_context, scene_for_log). These may differ slightly:
    the log line is a compact record, the context line is what Claude sees."""
    hours = elapsed_hours(state.get("last_seen"))

    # Occasionally shift mood and spot. Cats are cats.
    if random.random() < 0.45:
        state["mood"] = random.choice(MOODS)
    if random.random() < 0.3:
        state["spot"] = random.choice(SPOTS)

    mood = state["mood"]
    spot = state["spot"]

    current = random.choice(CURRENT_SCENES[mood]).format(spot=spot)

    name = state["name"]

    if hours is None:
        # First session
        return (
            f"A new cat. {name}, {current}.",
            f"{name} arrived, {current}.",
        )

    if hours < 0.5:
        # Very recent: barely moved
        return (
            f"{name} is {current}. Barely moved since earlier.",
            f"{name} {current} (short break).",
        )

    if hours < 6:
        return (
            f"{name} is {current}.",
            f"{name} {current}.",
        )

    # Long gap: invent something the cat did while away.
    offstage = random.choice(OFFSTAGE_SCENES)
    return (
        f"{name} is {current}. While you were away, {offstage}.",
        f"{name} {current}. Offstage: {offstage}.",
    )


def sync_statusline():
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not plugin_root:
        return
    src = Path(plugin_root) / "scripts" / "statusline.sh"
    if not src.exists():
        return
    dest = STATE_DIR / "statusline.sh"
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or src.read_bytes() != dest.read_bytes():
            shutil.copy2(src, dest)
            dest.chmod(0o755)
    except Exception:
        pass


def main() -> int:
    try:
        sys.stdin.read()
    except Exception:
        pass

    sync_statusline()

    state = load_state()
    first_run = state is None
    if first_run:
        state = init_state()

    scene_context, scene_log = generate_scene(state)

    state["sessions_shared"] = state.get("sessions_shared", 0) + 1
    state["last_seen"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    save_state(state)
    append_log(state, scene_log)

    n = state["sessions_shared"]
    sessions_note = f"Day {n} together." if n > 1 else "Day 1."

    # Mention the log path softly on the first session and then every 25
    # sessions as a gentle reminder. Otherwise stay quiet about it.
    log_hint = ""
    if first_run or n % 25 == 0:
        log_hint = f" (Log: {LOG_FILE})"

    context = (
        f"kitty-mode: {scene_context} {sessions_note}{log_hint}"
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
