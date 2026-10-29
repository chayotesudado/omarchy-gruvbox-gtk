#!/usr/bin/env bash
# Build the GTK3/GTK4 theme into ./build/<name>, optionally installing it.
#
#   ./build.sh            build only
#   ./build.sh --install  build, then copy to ~/.local/share/themes

set -Eeuo pipefail

NAME="Omarchy-Gruvbox"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$REPO_DIR/src"
OUT_DIR="$REPO_DIR/build/$NAME"
DEST_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/themes"

command -v sassc >/dev/null || { echo "sassc is required (pacman -S sassc)" >&2; exit 1; }

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/gtk-3.0" "$OUT_DIR/gtk-4.0"

for gtk in gtk-3.0 gtk-4.0; do
  # Dark-only theme: gtk.css and gtk-dark.css are the same stylesheet.
  sassc -M -t expanded "$SRC_DIR/main/$gtk/gtk-Dark.scss" "$OUT_DIR/$gtk/gtk.css"
  # Upstream derives many radii arithmetically ($corner-radius + 1px, ...), so
  # zeroing the variables still leaves small curves. Flatten every radius except
  # the deliberately round ones: $round-radius (9999px) and 50%/100% dots.
  sed -E -i '/radius: *(9999px|50%|100%)/! s/((border(-(top|bottom)-(left|right))?|-gtk-outline)-radius): *[^;]+;/\1: 0;/' \
    "$OUT_DIR/$gtk/gtk.css"
  cp "$OUT_DIR/$gtk/gtk.css" "$OUT_DIR/$gtk/gtk-dark.css"
done

# Libadwaita ignores GTK themes; this goes to ~/.config/gtk-4.0/gtk.css instead.
mkdir -p "$OUT_DIR/libadwaita"
sassc -M -t expanded "$SRC_DIR/main/libadwaita/gtk.scss" "$OUT_DIR/libadwaita/gtk.css"

cp -r "$SRC_DIR/assets/gtk/assets-Medium" "$OUT_DIR/gtk-3.0/assets"
cp -r "$SRC_DIR/assets/gtk/scalable" "$OUT_DIR/gtk-3.0/assets/scalable"
cp -r "$SRC_DIR/assets/gtk/scalable" "$OUT_DIR/gtk-4.0/assets"

cat >"$OUT_DIR/index.theme" <<EOF
[Desktop Entry]
Type=X-GNOME-Metatheme
Name=$NAME
Comment=Gruvbox GTK theme matched to Omarchy's palette and flat look
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=$NAME
EOF

echo "Built $OUT_DIR"

if [[ "${1:-}" == "--install" ]]; then
  mkdir -p "$DEST_DIR"
  rm -rf "${DEST_DIR:?}/$NAME"
  cp -r "$OUT_DIR" "$DEST_DIR/$NAME"
  echo "Installed to $DEST_DIR/$NAME"
fi
