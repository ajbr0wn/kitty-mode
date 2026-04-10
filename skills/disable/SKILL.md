---
name: disable
description: Turn off kitty-mode. Removes the walking-cat statusline and restores any previous statusLine.
allowed-tools: [Read, Write, Edit, Bash]
---

# Disable kitty-mode

Remove the kitty-mode statusline from the user's Claude Code settings.

## Steps

### 1. Read the user's settings

Read `~/.claude/settings.json`. If it doesn't exist or has no `statusLine` at all, tell the user kitty-mode wasn't active and stop.

### 2. Restore or clear the statusLine

Parse the JSON:

- If `_kitty_mode_previous_statusLine` exists, move it back to `statusLine` (replacing the kitty-mode one) and delete the `_kitty_mode_previous_statusLine` key.
- Otherwise, just delete the `statusLine` key entirely.
- Write the file back with pretty-printed JSON (2-space indent).

Use the Read + Write tools directly. Don't shell out to `jq`.

If you encounter JSON parse errors on the existing settings, STOP and tell the user to fix the file manually. Do not clobber their settings.

### 3. Confirm to the user

Tell the user:

- kitty-mode is now disabled
- If a previous statusLine was restored, mention it
- The stable script at `~/.claude/kitty-mode/statusline.sh` is left in place so `/kitty-mode:enable` can turn things back on quickly. Mention it can be manually deleted if they want a clean slate.

Keep it short and kind. A small wave from the cat (`(=^..^=) ~`) is allowed but optional.
