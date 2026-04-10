---
name: enable
description: Turn on kitty-mode. Installs the walking-cat statusline into ~/.claude/settings.json, backing up any existing statusLine.
allowed-tools: [Read, Write, Edit, Bash]
---

# Enable kitty-mode

Install the kitty-mode statusline into the user's Claude Code settings.

## What you're doing

1. Sync the bundled statusline script to a stable path at `~/.claude/kitty-mode/statusline.sh` so that future plugin updates don't break the installed path.
2. Edit `~/.claude/settings.json` to set `statusLine` to run that script, with `refreshInterval: 1` so the cat walks smoothly.
3. Back up any pre-existing `statusLine` into a `_kitty_mode_previous_statusLine` key on the same object, so `/kitty-mode:disable` can restore it.

## Steps

### 1. Sync the statusline script

Run this to ensure the stable copy exists and is up to date:

```bash
mkdir -p ~/.claude/kitty-mode && cp "${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh" ~/.claude/kitty-mode/statusline.sh && chmod +x ~/.claude/kitty-mode/statusline.sh
```

### 2. Read the user's settings

Read `~/.claude/settings.json`. If it doesn't exist, you'll be creating it.

### 3. Update settings

Parse the JSON, then:

- If the file has an existing `statusLine` field that is NOT already the kitty-mode one, copy it to `_kitty_mode_previous_statusLine` so disable can restore it. Do NOT overwrite an existing `_kitty_mode_previous_statusLine` (the user may have run enable twice, in which case the first backup is the real one).
- Set `statusLine` to:
  ```json
  {
    "type": "command",
    "command": "~/.claude/kitty-mode/statusline.sh",
    "refreshInterval": 1,
    "padding": 1
  }
  ```
- Write the file back with pretty-printed JSON (2-space indent) to keep it readable.

Use the Read tool then the Write tool. Do not use `jq`, since it may not be installed and the user's settings may have comments or unusual formatting you should preserve carefully.

If you encounter JSON parse errors on the existing settings, STOP and tell the user to fix the file manually. Do not clobber their settings.

### 4. Confirm to the user

Tell the user:

- kitty-mode is now enabled
- The cat will appear in the status bar on the next assistant response
- If they had a previous statusLine, mention it was backed up and can be restored with `/kitty-mode:disable`
- Remind them `/kitty-mode:disable` turns it off

Keep the confirmation short and warm. A small `🐈` at the end is fine.

## Notes

- The `CLAUDE_PLUGIN_ROOT` env var is available in your Bash calls because this skill runs inside a plugin.
- `refreshInterval: 1` means the statusline re-runs every second so the cat walks smoothly. Without it, the cat still moves (once per assistant turn) but much more slowly.
- If settings.json already has a kitty-mode statusLine, just re-sync the script (no settings changes needed) and tell the user it's already enabled.
