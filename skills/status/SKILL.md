---
name: status
description: Check whether kitty-mode is currently active and show a preview of the statusline.
allowed-tools: [Read, Bash]
---

# kitty-mode status

Check whether kitty-mode is currently installed, and show a preview.

## Steps

### 1. Read the user's settings

Read `~/.claude/settings.json`.

- If there's no `statusLine` field: report "kitty-mode is not enabled. Run `/kitty-mode:enable` to turn it on."
- If `statusLine.command` points at `~/.claude/kitty-mode/statusline.sh` (or contains `kitty-mode/statusline.sh`): report "kitty-mode is enabled 🐈".
- Otherwise: report "A different statusLine is active. kitty-mode is not installed. `/kitty-mode:enable` will back up the current statusLine before installing."

### 2. Show a preview (optional but nice)

If kitty-mode is enabled, run this to render what the cat currently looks like:

```bash
echo '{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$PWD"'"},"context_window":{"used_percentage":42}}' | ~/.claude/kitty-mode/statusline.sh
```

Print the output in a code block so the user can see it.

### 3. Report

Keep it short. If there was a `_kitty_mode_previous_statusLine` in settings, mention it in one line so the user remembers they have a backup.
