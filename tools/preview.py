#!/usr/bin/env python3
"""Widget gallery for eyeballing the theme.

    tools/preview.py gtk4      plain GTK4 (uses the GTK theme)
    tools/preview.py adw       libadwaita (uses ~/.config/gtk-4.0/gtk.css)
    tools/preview.py gtk3      GTK3

Pass --popover to open a menu popover once the window is shown, and
--quit-after SECONDS to close on its own (handy for screenshots).
"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("toolkit", choices=["gtk4", "adw", "gtk3"])
parser.add_argument("--popover", action="store_true")
parser.add_argument("--quit-after", type=float, default=0)
args = parser.parse_args()

import gi  # noqa: E402

TITLE = f"theme-preview-{args.toolkit}"

if args.toolkit == "gtk3":
    gi.require_version("Gtk", "3.0")
    from gi.repository import GLib, Gtk

    def gtk3_main():
        win = Gtk.Window(title=TITLE)
        win.set_default_size(900, 640)
        win.connect("destroy", Gtk.main_quit)

        header = Gtk.HeaderBar(title=TITLE, show_close_button=True)
        header.pack_start(Gtk.Button(label="Open"))
        menu_button = Gtk.MenuButton()
        menu = Gtk.Menu()
        for label in ("New Window", "Preferences", "About"):
            menu.append(Gtk.MenuItem(label=label))
        menu.show_all()
        menu_button.set_popup(menu)
        header.pack_end(menu_button)
        win.set_titlebar(header)

        paned = Gtk.Paned()
        sidebar = Gtk.ListBox()
        sidebar.get_style_context().add_class("navigation-sidebar")
        for name in ("Home", "Documents", "Downloads", "Music", "Pictures"):
            sidebar.add(Gtk.Label(label=name, xalign=0, margin=8))
        sidebar.select_row(sidebar.get_row_at_index(1))
        paned.pack1(sidebar, False, False)

        grid = Gtk.Grid(column_spacing=12, row_spacing=12, margin=24)
        row = 0

        def add(*widgets):
            nonlocal row
            for col, w in enumerate(widgets):
                if not w.get_hexpand():
                    w.set_halign(Gtk.Align.START)
                    w.set_valign(Gtk.Align.CENTER)
                grid.attach(w, col, row, 1, 1)
            row += 1

        suggested = Gtk.Button(label="Suggested")
        suggested.get_style_context().add_class("suggested-action")
        destructive = Gtk.Button(label="Destructive")
        destructive.get_style_context().add_class("destructive-action")
        add(Gtk.Button(label="Button"), suggested, destructive)
        toggle = Gtk.ToggleButton(label="Toggled", active=True)
        flat = Gtk.Button(label="Flat")
        flat.set_relief(Gtk.ReliefStyle.NONE)
        insensitive = Gtk.Button(label="Disabled", sensitive=False)
        add(toggle, flat, insensitive)
        entry = Gtk.Entry(placeholder_text="Entry")
        add(entry, Gtk.SearchEntry(), Gtk.SpinButton.new_with_range(0, 100, 1))
        radio1 = Gtk.RadioButton(label="Radio")
        radio2 = Gtk.RadioButton(label="Radio", group=radio1, active=True)
        add(Gtk.CheckButton(label="Check", active=True), radio1, radio2)
        sw = Gtk.Switch(active=True)
        combo = Gtk.ComboBoxText()
        for item in ("Combo", "Second"):
            combo.append_text(item)
        combo.set_active(0)
        add(sw, Gtk.Switch(), combo)
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        scale.set_value(60)
        scale.set_hexpand(True)
        progress = Gtk.ProgressBar(fraction=0.4)
        progress.set_hexpand(True)
        add(scale, progress, Gtk.LevelBar(value=0.7, hexpand=True))
        notebook = Gtk.Notebook()
        for tab in ("General", "Appearance", "Advanced"):
            notebook.append_page(Gtk.Label(label=f"{tab} page", margin=24), Gtk.Label(label=tab))
        grid.attach(notebook, 0, row, 3, 1)
        row += 1
        text = Gtk.TextView()
        text.get_buffer().set_text("Text view with a selection")
        buf = text.get_buffer()
        buf.select_range(buf.get_iter_at_offset(17), buf.get_iter_at_offset(26))
        frame = Gtk.Frame()
        frame.add(text)
        grid.attach(frame, 0, row, 3, 1)

        paned.pack2(grid, True, False)
        win.add(paned)
        win.show_all()

        if args.popover:
            GLib.timeout_add(600, lambda: (menu_button.clicked(), False)[1])
        if args.quit_after:
            GLib.timeout_add(int(args.quit_after * 1000), lambda: (Gtk.main_quit(), False)[1])
        Gtk.main()

    gtk3_main()
    raise SystemExit

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk  # noqa: E402

if args.toolkit == "adw":
    gi.require_version("Adw", "1")
    from gi.repository import Adw

    App = Adw.Application
else:
    App = Gtk.Application


def menu_model():
    menu = Gio.Menu()
    menu.append("New Window", "app.noop")
    menu.append("Preferences", "app.noop")
    section = Gio.Menu()
    section.append("Keyboard Shortcuts", "app.noop")
    section.append("About", "app.noop")
    menu.append_section(None, section)
    return menu


def controls():
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    for m in ("margin_top", "margin_bottom", "margin_start", "margin_end"):
        box.set_property(m, 24)

    def row(*widgets):
        r = Gtk.Box(spacing=12)
        for w in widgets:
            r.append(w)
        box.append(r)

    row(
        Gtk.Button(label="Button"),
        Gtk.Button(label="Suggested", css_classes=["suggested-action"]),
        Gtk.Button(label="Destructive", css_classes=["destructive-action"]),
        Gtk.ToggleButton(label="Toggled", active=True),
        Gtk.Button(label="Flat", css_classes=["flat"]),
        Gtk.Button(label="Disabled", sensitive=False),
    )
    row(
        Gtk.Entry(placeholder_text="Entry"),
        Gtk.SearchEntry(),
        Gtk.SpinButton.new_with_range(0, 100, 1),
        Gtk.DropDown.new_from_strings(["Dropdown", "Second", "Third"]),
    )
    check = Gtk.CheckButton(label="Check", active=True)
    radio1 = Gtk.CheckButton(label="Radio")
    radio2 = Gtk.CheckButton(label="Radio", group=radio1, active=True)
    row(check, radio1, radio2, Gtk.Switch(active=True), Gtk.Switch())
    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    scale.set_value(60)
    scale.set_hexpand(True)
    progress = Gtk.ProgressBar(fraction=0.4, hexpand=True, valign=Gtk.Align.CENTER)
    row(scale, progress)

    if args.toolkit == "adw":
        group = Adw.PreferencesGroup(title="Preferences group")
        group.add(Adw.ActionRow(title="Action row", subtitle="With a subtitle"))
        group.add(Adw.SwitchRow(title="Switch row", active=True))
        group.add(Adw.EntryRow(title="Entry row"))
        group.add(Adw.ComboRow(title="Combo row", model=Gtk.StringList.new(["One", "Two"])))
        box.append(group)
    else:
        notebook = Gtk.Notebook()
        for tab in ("General", "Appearance", "Advanced"):
            notebook.append_page(Gtk.Label(label=f"{tab} page", margin_top=24, margin_bottom=24), Gtk.Label(label=tab))
        box.append(notebook)

    text = Gtk.TextView(height_request=60)
    buf = text.get_buffer()
    buf.set_text("Text view with a selection")
    buf.select_range(buf.get_iter_at_offset(17), buf.get_iter_at_offset(26))
    box.append(Gtk.Frame(child=text))
    return box


def sidebar():
    lb = Gtk.ListBox(css_classes=["navigation-sidebar"])
    for name in ("Home", "Documents", "Downloads", "Music", "Pictures"):
        lb.append(Gtk.Label(label=name, xalign=0))
    lb.select_row(lb.get_row_at_index(1))
    return lb


def on_activate(app):
    app.add_action(Gio.SimpleAction.new("noop", None))
    menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu_model())

    if args.toolkit == "adw":
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        win = Adw.ApplicationWindow(application=app, title=TITLE, default_width=1000, default_height=720)
        side_header = Adw.HeaderBar()
        side_page = Adw.ToolbarView(content=sidebar())
        side_page.add_top_bar(side_header)
        content_header = Adw.HeaderBar()
        content_header.pack_start(Gtk.Button(label="Open"))
        content_header.pack_end(menu_button)
        content = Adw.ToolbarView(content=Gtk.ScrolledWindow(child=controls()))
        content.add_top_bar(content_header)
        split = Adw.NavigationSplitView(
            sidebar=Adw.NavigationPage(child=side_page, title="Sidebar"),
            content=Adw.NavigationPage(child=content, title=TITLE),
        )
        win.set_content(split)
    else:
        win = Gtk.ApplicationWindow(application=app, title=TITLE, default_width=1000, default_height=720)
        header = Gtk.HeaderBar()
        header.pack_start(Gtk.Button(label="Open"))
        header.pack_end(menu_button)
        win.set_titlebar(header)
        paned = Gtk.Paned(start_child=sidebar(), end_child=controls(), position=180)
        win.set_child(paned)

    win.present()
    if args.popover:
        GLib.timeout_add(600, lambda: (menu_button.popup(), False)[1])
    if args.quit_after:
        GLib.timeout_add(int(args.quit_after * 1000), lambda: (app.quit(), False)[1])


app = App(application_id=f"org.omarchy.ThemePreview.{args.toolkit.capitalize()}", flags=Gio.ApplicationFlags.NON_UNIQUE)
app.connect("activate", on_activate)
app.run(None)
