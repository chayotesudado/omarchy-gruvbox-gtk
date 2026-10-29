#!/usr/bin/env bash
# Screenshot the preview gallery on Hyprland.
#
#   tools/screenshot.sh <gtk4|adw|gtk3> <out.png> [--popover]
#
# The window opens floating at a fixed size on the current workspace, is
# captured with grim, and closes itself.

set -Eeuo pipefail

toolkit="$1"
out="$2"
shift 2

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
title="theme-preview-$toolkit"

python3 -I "$dir/preview.py" "$toolkit" --quit-after 5 "$@" &
pid=$!

addr=""
for _ in $(seq 40); do
  addr=$(hyprctl clients -j | python3 -I -c '
import json, sys
title = sys.argv[1]
for c in json.load(sys.stdin):
    if c["title"] == title:
        print(c["address"])
        break
' "$title")
  [[ -n "$addr" ]] && break
  sleep 0.1
done
[[ -n "$addr" ]] || { echo "preview window never appeared" >&2; kill "$pid"; exit 1; }

# Hyprland 0.55+ takes Lua dispatches; older versions take the classic syntax.
window="address:$addr"
hypr_dispatch() {
  local lua="$1"
  shift
  hyprctl dispatch "$lua" >/dev/null 2>&1 || hyprctl dispatch "$@" >/dev/null
}
hypr_dispatch "hl.dsp.window.float({ window = \"$window\", action = \"toggle\" })" togglefloating "$window"
hypr_dispatch "hl.dsp.window.resize({ window = \"$window\", x = 1000, y = 720 })" resizewindowpixel "exact 1000 720,$window"
hypr_dispatch "hl.dsp.window.center({ window = \"$window\" })" centerwindow
# Omarchy makes windows slightly translucent; screenshots should show true colors.
hypr_dispatch "hl.dsp.window.set_prop({ window = \"$window\", prop = \"opaque\", value = \"1\" })" setprop "$window" opaque 1
sleep 2.4

box=$(hyprctl clients -j | python3 -I -c '
import json, sys
for c in json.load(sys.stdin):
    if c["address"] == sys.argv[1]:
        (x, y), (w, h) = c["at"], c["size"]
        print(f"{x},{y} {w}x{h}")
' "$addr")
grim -g "$box" "$out"
wait "$pid" || true
echo "$out"
