# kitty-mode

An ambient companion cat that walks across your Claude Code status bar.

Inspired by Google Colab's kitty mode.

```
[Opus 4.6] · my-project 42%
              🐈
```

## Install

```bash
claude --plugin-dir /path/to/kitty-mode
```

Then inside Claude Code:

```
/kitty-mode:enable
```

The cat will appear in the status bar on the next assistant response. Use `/kitty-mode:disable` to turn it off (restores any previous statusline).

## What it does

- **A walking cat in the status bar.** Alternates between 🐈 and a few ASCII poses (`=^..^=`, `~(=^.^)`, `(=^.^=)`).
- **A small awareness note in Claude's session context** at SessionStart, so whichever Claude is in the session knows there's a companion cat around.

## Slash commands

- `/kitty-mode:enable` — installs the statusline, backs up any existing one
- `/kitty-mode:disable` — restores your previous statusline
- `/kitty-mode:status` — shows whether it's active, with a preview

## Requirements

- `python3` on PATH (for JSON parsing in the statusline script)
- A terminal that renders ANSI colors and unicode

## Credits

Idea: [@ajbr0wn](https://github.com/ajbr0wn). Build: Claude (Opus 4.6). Cat: nature.
