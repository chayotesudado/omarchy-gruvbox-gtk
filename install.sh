#!/usr/bin/env bash
# Build and install Omarchy-Gruvbox for GTK3, GTK4 and libadwaita.
#
#   ./install.sh              install and switch to the theme
#   ./install.sh --uninstall  remove it and restore the previous gtk-4.0 CSS

set -Eeuo pipefail

NAME="Omarchy-Gruvbox"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEMES_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/themes"
GTK4_CSS="${XDG_CONFIG_HOME:-$HOME/.config}/gtk-4.0/gtk.css"
BACKUP="$GTK4_CSS.before-omarchy-gruvbox"
MARKER="Libadwaita layer, installed as ~/.config/gtk-4.0/gtk.css"

if [[ "${1:-}" == "--uninstall" ]]; then
  rm -rf "${THEMES_DIR:?}/$NAME"
  if [[ -f "$BACKUP" ]]; then
    mv "$BACKUP" "$GTK4_CSS"
    echo "Restored $GTK4_CSS"
  elif [[ -f "$GTK4_CSS" ]] && grep -qF "$MARKER" "$GTK4_CSS"; then
    rm "$GTK4_CSS"
  fi
  gsettings reset org.gnome.desktop.interface gtk-theme
  echo "Uninstalled $NAME"
  exit 0
fi

"$REPO_DIR/build.sh" --install

# Libadwaita only reads ~/.config/gtk-4.0/gtk.css. Keep whatever was there
# the first time, unless it is a previous copy of this theme.
mkdir -p "$(dirname "$GTK4_CSS")"
if [[ -f "$GTK4_CSS" && ! -f "$BACKUP" ]] && ! grep -qF "$MARKER" "$GTK4_CSS"; then
  cp "$GTK4_CSS" "$BACKUP"
  echo "Backed up existing $GTK4_CSS to $BACKUP"
fi
cp "$REPO_DIR/build/$NAME/libadwaita/gtk.css" "$GTK4_CSS"

gsettings set org.gnome.desktop.interface gtk-theme "$NAME"
gsettings set org.gnome.desktop.interface color-scheme prefer-dark

echo "Done. Restart open GTK apps to pick up the theme."
