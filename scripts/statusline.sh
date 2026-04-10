#!/bin/bash
# kitty-mode statusline
#
# Reads Claude Code session JSON on stdin and prints a two-line status: an
# info line (model, cwd, context %) and an ambient walking cat.
#
# The cat frame advances each invocation. With refreshInterval=1 in
# ~/.claude/settings.json the cat walks smoothly; without it, the cat takes
# one step each time Claude responds.

set -u

input=$(cat)

# Parse JSON with python3 (jq isn't always installed).
eval "$(python3 - "$input" <<'PY'
import json, os, sys, shlex
raw = sys.argv[1] if len(sys.argv) > 1 else ""
try:
    d = json.loads(raw) if raw else {}
except Exception:
    d = {}

def g(path, default=""):
    cur = d
    for p in path.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur if cur is not None else default

model = g("model.display_name", "Claude")
cwd = g("workspace.current_dir") or g("cwd") or os.getcwd()
pct = g("context_window.used_percentage", 0)
try:
    pct = int(float(pct))
except Exception:
    pct = 0

basename = os.path.basename(cwd.rstrip("/")) or "/"
print(f"MODEL={shlex.quote(str(model))}")
print(f"DIRNAME={shlex.quote(basename)}")
print(f"PCT={pct}")
PY
)"

# Frame counter: nudged each invocation so the cat moves even without
# refreshInterval. Time is mixed in so refreshInterval=1 produces smooth
# motion.
STATE_DIR="${CLAUDE_PLUGIN_DATA:-${TMPDIR:-/tmp}}"
mkdir -p "$STATE_DIR" 2>/dev/null
STATE_FILE="$STATE_DIR/kitty-frame"
NUDGE=0
[ -f "$STATE_FILE" ] && NUDGE=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
NUDGE=$(( (NUDGE + 1) % 10000 ))
echo "$NUDGE" > "$STATE_FILE" 2>/dev/null || true
FRAME=$(( $(date +%s) + NUDGE ))

# Colors
PINK=$'\033[38;5;213m'
CYAN=$'\033[38;5;117m'
DIM=$'\033[38;5;245m'
YELLOW=$'\033[38;5;222m'
RESET=$'\033[0m'

# Info line
printf '%b[%s]%b %b·%b %b%s%b %b%d%%%b\n' \
  "$PINK" "$MODEL" "$RESET" \
  "$DIM" "$RESET" \
  "$CYAN" "$DIRNAME" "$RESET" \
  "$YELLOW" "$PCT" "$RESET"

# Kitty line: cat walks a fixed track, ping-ponging at the edges.
TRACK_WIDTH=36

SUBFRAME=$(( FRAME % 8 ))
case "$SUBFRAME" in
  3) CAT="=^..^=" ;;
  6) CAT="~(=^.^)" ;;
  7) CAT="(=^.^=)" ;;
  *) CAT=$'\xf0\x9f\x90\x88' ;;   # 🐈
esac

STEP=$(( FRAME / 2 ))
CYCLE=$(( TRACK_WIDTH * 2 ))
POS=$(( STEP % CYCLE ))
[ "$POS" -ge "$TRACK_WIDTH" ] && POS=$(( CYCLE - POS - 1 ))
[ "$POS" -lt 0 ] && POS=0
[ "$POS" -gt "$TRACK_WIDTH" ] && POS="$TRACK_WIDTH"

# Build left padding
LEFT=""
i=0
while [ "$i" -lt "$POS" ]; do LEFT+=" "; i=$(( i + 1 )); done

printf '%b%s%b%s\n' "$DIM" "$LEFT" "$RESET" "$CAT"
