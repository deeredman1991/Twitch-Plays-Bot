import os
import io
import json

from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from scripts.screen import Screen


class Settings(Screen):
    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.created = False

        self._active_page = 'twitch'
        self._active_bindings_kind = 'aliases_buttons'

        self._content_holder = None
        self._status_label = None

        self._twitch_inputs = {}
        self._emu_inputs = {}
        self._binding_rows = []
        self._axes_comment = None
        self._plugin_binding_inputs = {}

        self._hover_targets = []
        self._hover_active_text = None
        self._hover_bound = False

        self._rt_command_rows = []
        self._rt_reset_to_defaults = False

    def on_enter(self):
        if not self.created:
            self._build_ui()
            self.created = True

        self.reload_from_files()
        self.show_page(self._active_page)

    def _profile_dir(self):
        return os.path.join(self.parent.cfg_path, self.parent.profile)

    def _file_path(self, key):
        return os.path.join(self._profile_dir(), key + '.json')

    def _set_status(self, msg):
        try:
            self._status_label.text = msg
        except Exception:
            pass

    def back_button_on_press(self):
        self.parent.current = 'Main Menu'

    def _build_ui(self):
        root = self.make_box(self)

        nav = self.make_box(root, o='horizontal', sy=0.12)
        self.make_button(nav, 'Twitch', lambda *a: self.show_page('twitch'), sx=0.25, sy=1)
        self.make_button(nav, 'Emulator', lambda *a: self.show_page('emulator'), sx=0.25, sy=1)
        self.make_button(nav, 'Bindings', lambda *a: self.show_page('bindings'), sx=0.25, sy=1)
        self.make_button(nav, 'Plugins', lambda *a: self.show_page('plugins'), sx=0.25, sy=1)

        status_row = self.make_box(root, o='horizontal', sy=0.08)
        self._status_label = Label(text='')
        status_row.add_widget(self._status_label)

        self._content_holder = self.make_box(root, sy=0.70)

        bottom = self.make_box(root, o='horizontal', sy=0.10)
        self.make_button(bottom, 'Reload', lambda *a: self.reload_from_files(), sx=0.25, sy=1)
        self.make_button(bottom, 'Save', lambda *a: self.save_active_page(), sx=0.25, sy=1)
        self.make_button(bottom, 'Back', self.back_button_on_press, sx=0.25, sy=1)
        self.make_box(bottom, sx=0.25, sy=1)

        if not self._hover_bound:
            Window.bind(mouse_pos=self._on_mouse_pos)
            self._hover_bound = True

    def _on_mouse_pos(self, _window, pos):
        if self._status_label is None:
            return

        x, y = pos
        hovered_text = None

        def _collide_window(widget, mx, my):
            try:
                lx, ly = widget.to_widget(mx, my, relative=False)
                return widget.collide_point(lx, ly)
            except Exception:
                return False

        for widget, text in list(self._hover_targets):
            try:
                if widget is None or widget.get_parent_window() is None:
                    continue
                if _collide_window(widget, x, y):
                    hovered_text = text
                    break
            except Exception:
                continue

        if hovered_text != self._hover_active_text:
            self._hover_active_text = hovered_text
            if hovered_text:
                self._set_status(hovered_text)

    def show_page(self, page):
        self._active_page = page

        if self._content_holder is None:
            return

        self._content_holder.clear_widgets()

        if page == 'twitch':
            self._content_holder.add_widget(self._build_twitch_page())
        elif page == 'emulator':
            self._content_holder.add_widget(self._build_emulator_page())
        elif page == 'bindings':
            self._content_holder.add_widget(self._build_bindings_page())
        else:
            self._content_holder.add_widget(self._build_plugins_page())

    def _read_json(self, key):
        path = self._file_path(key)
        with io.open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_json(self, key, obj):
        path = self._file_path(key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp_path = path + '.tmp'
        with io.open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)

    def reload_from_files(self):
        try:
            login = self._read_json('login')
        except Exception:
            login = {}
        try:
            emu = self._read_json('emulator_settings')
        except Exception:
            emu = {}
        try:
            axes = self._read_json('aliases_axes')
        except Exception:
            axes = {}

        self._axes_comment = axes.get('_comment')

        if 'bot_name' in self._twitch_inputs:
            self._twitch_inputs['bot_name'].text = str(login.get('bot_name', ''))
            self._twitch_inputs['bot_oAuth'].text = str(login.get('bot_oAuth', ''))
            self._twitch_inputs['streamer_name'].text = str(login.get('streamer_name', ''))

        if 'emu_path' in self._emu_inputs:
            self._emu_inputs['emu_path'].text = str(emu.get('emu_path', ''))
            self._emu_inputs['process_name'].text = str(emu.get('process_name', ''))
            self._emu_inputs['pid'].active = bool(emu.get('pid', False))

        self._set_status('Loaded profile: {}'.format(self.parent.profile))

    def save_active_page(self):
        if self._active_page == 'twitch':
            self._save_twitch()
        elif self._active_page == 'emulator':
            self._save_emulator()
        elif self._active_page == 'bindings':
            self._save_bindings()
        else:
            self._set_status('Plugins settings save automatically')

    def _build_plugins_page(self):
        root = BoxLayout(orientation='vertical')

        plugin_manager = getattr(self.parent, 'plugin_manager', None)
        if plugin_manager is None:
            root.add_widget(Label(text='Plugin manager not available', size_hint_y=None, height=44))
            return root

        root.add_widget(Label(text='Enable/Disable plugins (restart app to apply changes)', size_hint_y=None, height=44))

        infos = plugin_manager.infos()
        if not infos:
            root.add_widget(Label(text='No plugins found in /plugins', size_hint_y=None, height=44))
            return root

        rows = GridLayout(cols=1, size_hint_y=None)
        rows.bind(minimum_height=rows.setter('height'))

        sv = ScrollView(do_scroll_x=False)
        sv.add_widget(rows)
        root.add_widget(sv)

        for plugin_id in sorted(infos.keys()):
            info = infos[plugin_id]
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)

            label_text = '{} ({}) v{}'.format(info.name, info.plugin_id, info.version)
            if getattr(info, 'error', None):
                label_text = label_text + ' [ERROR]'

            row.add_widget(Label(text=label_text, size_hint_x=0.70))

            switch = Switch(active=plugin_manager.is_enabled(plugin_id), size_hint_x=0.15)
            details = Button(text='Details', size_hint_x=0.15)

            def _toggle(_switch, value, pid=plugin_id):
                plugin_manager.set_enabled(pid, bool(value))
                self._set_status('Plugin {} set to {} (restart required)'.format(pid, 'enabled' if value else 'disabled'))

            def _details(_btn, pid=plugin_id):
                i = plugin_manager.infos().get(pid)
                if i is None:
                    return
                err = getattr(i, 'error', None)
                if err:
                    self._set_status('Plugin error: {}'.format(err.splitlines()[-1] if isinstance(err, str) else err))
                else:
                    self._set_status('Plugin ok: {}'.format(pid))

            switch.bind(active=_toggle)
            details.bind(on_press=_details)

            row.add_widget(switch)
            row.add_widget(details)
            rows.add_widget(row)

        return root

    def _build_twitch_page(self):
        root = BoxLayout(orientation='vertical')
        grid = GridLayout(cols=2, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        def add_field(label_text, key, password=False):
            grid.add_widget(Label(text=label_text, size_hint_y=None, height=44))
            ti = TextInput(multiline=False, password=password, size_hint_y=None, height=44)
            self._twitch_inputs[key] = ti
            grid.add_widget(ti)

        add_field('Bot Name', 'bot_name')
        add_field('Bot OAuth', 'bot_oAuth', password=True)
        add_field('Streamer Name', 'streamer_name')

        sv = ScrollView(do_scroll_x=False)
        sv.add_widget(grid)
        root.add_widget(sv)
        return root

    def _build_emulator_page(self):
        root = BoxLayout(orientation='vertical')
        grid = GridLayout(cols=2, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        grid.add_widget(Label(text='Emulator Path', size_hint_y=None, height=44))
        emu_path = TextInput(multiline=False, size_hint_y=None, height=44)
        self._emu_inputs['emu_path'] = emu_path
        grid.add_widget(emu_path)

        grid.add_widget(Label(text='Process Name', size_hint_y=None, height=44))
        proc = TextInput(multiline=False, size_hint_y=None, height=44)
        self._emu_inputs['process_name'] = proc
        grid.add_widget(proc)

        grid.add_widget(Label(text='Use PID', size_hint_y=None, height=44))
        pid = CheckBox(size_hint_y=None, height=44)
        self._emu_inputs['pid'] = pid
        grid.add_widget(pid)

        sv = ScrollView(do_scroll_x=False)
        sv.add_widget(grid)
        root.add_widget(sv)
        return root

    def _build_bindings_page(self):
        root = BoxLayout(orientation='vertical')

        subnav = BoxLayout(orientation='horizontal', size_hint_y=0.15)
        subnav.add_widget(Button(text='Buttons', on_press=lambda *a: self._set_bindings_kind('aliases_buttons')))
        subnav.add_widget(Button(text='Axes', on_press=lambda *a: self._set_bindings_kind('aliases_axes')))
        subnav.add_widget(Button(text='D-Pad', on_press=lambda *a: self._set_bindings_kind('aliases_hats')))

        plugin_manager = getattr(self.parent, 'plugin_manager', None)
        if plugin_manager is not None:
            try:
                if plugin_manager.is_enabled('games.rogue_trader'):
                    subnav.add_widget(Button(text='Rogue Trader', on_press=lambda *a: self._set_bindings_kind('plugin:games.rogue_trader')))
            except Exception:
                pass
        root.add_widget(subnav)

        self._bindings_container = BoxLayout(orientation='vertical')
        root.add_widget(self._bindings_container)
        self._render_bindings_rows()

        footer = BoxLayout(orientation='horizontal', size_hint_y=0.15)
        footer.add_widget(Button(text='Add', on_press=lambda *a: self._add_binding_row('', '')))
        root.add_widget(footer)

        return root

    def _set_bindings_kind(self, kind):
        self._active_bindings_kind = kind
        self._render_bindings_rows()

    def _render_bindings_rows(self):
        if not hasattr(self, '_bindings_container') or self._bindings_container is None:
            return

        self._bindings_container.clear_widgets()
        self._binding_rows = []
        self._plugin_binding_inputs = {}
        self._hover_targets = []
        self._hover_active_text = None
        self._rt_command_rows = []

        if str(self._active_bindings_kind).startswith('plugin:'):
            self._render_plugin_bindings(str(self._active_bindings_kind).split(':', 1)[1])
            return

        try:
            data = self._read_json(self._active_bindings_kind)
        except Exception:
            data = {}

        if self._active_bindings_kind == 'aliases_axes':
            self._axes_comment = data.get('_comment', self._axes_comment)
            if self._axes_comment is not None:
                self._bindings_container.add_widget(Label(text=str(self._axes_comment), size_hint_y=None, height=44))

        rows_layout = GridLayout(cols=1, size_hint_y=None)
        rows_layout.bind(minimum_height=rows_layout.setter('height'))

        sv = ScrollView(do_scroll_x=False)
        sv.add_widget(rows_layout)
        self._bindings_container.add_widget(sv)

        for k in sorted(data.keys()):
            if k == '_comment':
                continue
            self._add_binding_row(str(k), str(data.get(k)), parent=rows_layout)

    def _get_rogue_trader_default_config(self):
        return {
            "enabled": True,
            "auto_install": True,
            "overwrite_existing": False,
            "prefix": "rt",
            "enable_help_command": True,
            "groups": {
                "movement": True,
                "camera": True,
                "ui": True,
                "combat": True,
                "safety": True
            },
            "defaults": {
                "move_hold": 0.8,
                "cam_hold": 0.4,
                "tap_hold": 0.2
            },
        }

    def _get_rogue_trader_default_commands(self):
        return {
            "!{p}_move_up #(hold_for=0.2:3)": ":tilt lx fd #(hold_for) smooth",
            "!{p}_move_down #(hold_for=0.2:3)": ":tilt lx bk #(hold_for) smooth",
            "!{p}_move_left #(hold_for=0.2:3)": ":tilt ly lf #(hold_for) smooth",
            "!{p}_move_right #(hold_for=0.2:3)": ":tilt ly ri #(hold_for) smooth",
            "!{p}_wu #(hold_for=0.2:3)": ":tilt lx fd #(hold_for) smooth",
            "!{p}_wd #(hold_for=0.2:3)": ":tilt lx bk #(hold_for) smooth",
            "!{p}_wl #(hold_for=0.2:3)": ":tilt ly lf #(hold_for) smooth",
            "!{p}_wr #(hold_for=0.2:3)": ":tilt ly ri #(hold_for) smooth",
            "!{p}_u": ":tilt lx fd 0.8 smooth",
            "!{p}_d": ":tilt lx bk 0.8 smooth",
            "!{p}_l": ":tilt ly lf 0.8 smooth",
            "!{p}_r": ":tilt ly ri 0.8 smooth",
            "!{p}_cam_up #(hold_for=0.1:2)": ":tilt rx fd #(hold_for) choppy",
            "!{p}_cam_down #(hold_for=0.1:2)": ":tilt rx bk #(hold_for) choppy",
            "!{p}_cam_left #(hold_for=0.1:2)": ":tilt ry lf #(hold_for) choppy",
            "!{p}_cam_right #(hold_for=0.1:2)": ":tilt ry ri #(hold_for) choppy",
            "!{p}_cu #(hold_for=0.1:2)": ":tilt rx fd #(hold_for) choppy",
            "!{p}_cd #(hold_for=0.1:2)": ":tilt rx bk #(hold_for) choppy",
            "!{p}_cl #(hold_for=0.1:2)": ":tilt ry lf #(hold_for) choppy",
            "!{p}_cr #(hold_for=0.1:2)": ":tilt ry ri #(hold_for) choppy",
            "!{p}_cu1": ":tilt rx fd 0.4 choppy",
            "!{p}_cd1": ":tilt rx bk 0.4 choppy",
            "!{p}_cl1": ":tilt ry lf 0.4 choppy",
            "!{p}_cr1": ":tilt ry ri 0.4 choppy",
            "!{p}_a #(hold_for=0.1:1)": ":mash x 1 0.1 #(hold_for)",
            "!{p}_b #(hold_for=0.1:1)": ":mash o 1 0.1 #(hold_for)",
            "!{p}_x #(hold_for=0.1:1)": ":mash s 1 0.1 #(hold_for)",
            "!{p}_y #(hold_for=0.1:1)": ":mash t 1 0.1 #(hold_for)",
            "!{p}_a1": ":mash x 1 0.1 0.2",
            "!{p}_b1": ":mash o 1 0.1 0.2",
            "!{p}_x1": ":mash s 1 0.1 0.2",
            "!{p}_y1": ":mash t 1 0.1 0.2",
            "!{p}_up #(hold_for=0.1:1)": ":hat 1 up 1 0.1 #(hold_for)",
            "!{p}_down #(hold_for=0.1:1)": ":hat 1 dn 1 0.1 #(hold_for)",
            "!{p}_left #(hold_for=0.1:1)": ":hat 1 lf 1 0.1 #(hold_for)",
            "!{p}_right #(hold_for=0.1:1)": ":hat 1 ri 1 0.1 #(hold_for)",
            "!{p}_menu": ":mash se 1 0.1 0.3",
            "!{p}_pause": ":mash se 1 0.1 0.3",
            "!{p}_end": ":mash st 1 0.1 0.3",
            "!{p}_endturn": ":mash st 1 0.1 0.3",
            "!{p}_rot_l #(hold_for=0.1:1)": ":mash l1 1 0.1 #(hold_for)",
            "!{p}_rot_r #(hold_for=0.1:1)": ":mash r1 1 0.1 #(hold_for)",
            "!{p}_zoom_in #(hold_for=0.1:1)": ":mash r2 1 0.1 #(hold_for)",
            "!{p}_zoom_out #(hold_for=0.1:1)": ":mash l2 1 0.1 #(hold_for)",
            "!{p}_next #(hold_for=0.1:1)": ":mash r3 1 0.1 #(hold_for)",
            "!{p}_prev #(hold_for=0.1:1)": ":mash l3 1 0.1 #(hold_for)",
            "!{p}_pon": ":set pausing 1",
            "!{p}_poff": ":set pausing 0",
            "!{p}_bindon": ":set binding 1",
            "!{p}_bindoff": ":set binding 0",
        }

    def _get_rogue_trader_default_labels(self):
        return {
            "!{p}_move_up #(hold_for=0.2:3)": "Move party/selection forward (Left Stick Up)",
            "!{p}_move_down #(hold_for=0.2:3)": "Move party/selection backward (Left Stick Down)",
            "!{p}_move_left #(hold_for=0.2:3)": "Strafe/step left (Left Stick Left)",
            "!{p}_move_right #(hold_for=0.2:3)": "Strafe/step right (Left Stick Right)",
            "!{p}_wu #(hold_for=0.2:3)": "Move forward (Left Stick Up)",
            "!{p}_wd #(hold_for=0.2:3)": "Move backward (Left Stick Down)",
            "!{p}_wl #(hold_for=0.2:3)": "Move left (Left Stick Left)",
            "!{p}_wr #(hold_for=0.2:3)": "Move right (Left Stick Right)",
            "!{p}_u": "Move forward (default duration)",
            "!{p}_d": "Move backward (default duration)",
            "!{p}_l": "Move left (default duration)",
            "!{p}_r": "Move right (default duration)",
            "!{p}_cam_up #(hold_for=0.1:2)": "Move camera up / tilt (Right Stick Up)",
            "!{p}_cam_down #(hold_for=0.1:2)": "Move camera down / tilt (Right Stick Down)",
            "!{p}_cam_left #(hold_for=0.1:2)": "Move camera left / rotate (Right Stick Left)",
            "!{p}_cam_right #(hold_for=0.1:2)": "Move camera right / rotate (Right Stick Right)",
            "!{p}_cu #(hold_for=0.1:2)": "Camera up (Right Stick Up)",
            "!{p}_cd #(hold_for=0.1:2)": "Camera down (Right Stick Down)",
            "!{p}_cl #(hold_for=0.1:2)": "Camera left (Right Stick Left)",
            "!{p}_cr #(hold_for=0.1:2)": "Camera right (Right Stick Right)",
            "!{p}_cu1": "Camera up (default duration)",
            "!{p}_cd1": "Camera down (default duration)",
            "!{p}_cl1": "Camera left (default duration)",
            "!{p}_cr1": "Camera right (default duration)",
            "!{p}_a #(hold_for=0.1:1)": "Confirm / Interact / Select (A button)",
            "!{p}_b #(hold_for=0.1:1)": "Cancel / Back / Close menu (B button)",
            "!{p}_x #(hold_for=0.1:1)": "Context action / secondary (X button)",
            "!{p}_y #(hold_for=0.1:1)": "Context action / tertiary (Y button)",
            "!{p}_a1": "Confirm / Interact (quick tap)",
            "!{p}_b1": "Cancel / Back (quick tap)",
            "!{p}_x1": "X button (quick tap)",
            "!{p}_y1": "Y button (quick tap)",
            "!{p}_up #(hold_for=0.1:1)": "Navigate up (D-Pad Up)",
            "!{p}_down #(hold_for=0.1:1)": "Navigate down (D-Pad Down)",
            "!{p}_left #(hold_for=0.1:1)": "Navigate left (D-Pad Left)",
            "!{p}_right #(hold_for=0.1:1)": "Navigate right (D-Pad Right)",
            "!{p}_menu": "Open menu / pause menu (Select)",
            "!{p}_pause": "Open menu / pause menu (Select)",
            "!{p}_end": "End turn / confirm turn end (Start)",
            "!{p}_endturn": "End turn / confirm turn end (Start)",
            "!{p}_rot_l #(hold_for=0.1:1)": "Rotate camera left (L1)",
            "!{p}_rot_r #(hold_for=0.1:1)": "Rotate camera right (R1)",
            "!{p}_zoom_in #(hold_for=0.1:1)": "Zoom camera in (R2)",
            "!{p}_zoom_out #(hold_for=0.1:1)": "Zoom camera out (L2)",
            "!{p}_next #(hold_for=0.1:1)": "Cycle next target/unit (R3)",
            "!{p}_prev #(hold_for=0.1:1)": "Cycle previous target/unit (L3)",
            "!{p}_pon": "Enable pausing mode (auto-pause after commands)",
            "!{p}_poff": "Disable pausing mode",
            "!{p}_bindon": "Enable binding mode (forces inputs to bind to game)",
            "!{p}_bindoff": "Disable binding mode",
        }

    def _render_plugin_bindings(self, plugin_id: str):
        plugin_manager = getattr(self.parent, 'plugin_manager', None)
        if plugin_manager is None:
            self._bindings_container.add_widget(Label(text='Plugin manager not available', size_hint_y=None, height=44))
            return

        defaults = None
        if plugin_id == 'games.rogue_trader':
            defaults = self._get_rogue_trader_default_config()
        else:
            defaults = {}

        cfg = {}
        try:
            cfg = plugin_manager.api.load_plugin_config(plugin_id=plugin_id, default=defaults)
        except Exception:
            cfg = dict(defaults or {})

        grid = GridLayout(cols=2, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        def add_text(label_text, key, value, hover_text=None):
            lbl = Label(text=label_text, size_hint_y=None, height=44)
            grid.add_widget(lbl)
            ti = TextInput(text=str(value), multiline=False, size_hint_y=None, height=44)
            self._plugin_binding_inputs[key] = ti
            grid.add_widget(ti)
            if hover_text:
                self._hover_targets.append((lbl, hover_text))
                self._hover_targets.append((ti, hover_text))

        def add_switch(label_text, key, value, hover_text=None):
            lbl = Label(text=label_text, size_hint_y=None, height=44)
            grid.add_widget(lbl)
            sw = Switch(active=bool(value), size_hint_y=None, height=44)
            self._plugin_binding_inputs[key] = sw
            grid.add_widget(sw)
            if hover_text:
                self._hover_targets.append((lbl, hover_text))
                self._hover_targets.append((sw, hover_text))

        if plugin_id == 'games.rogue_trader':
            add_text('Command Prefix', 'prefix', cfg.get('prefix', 'rt'), hover_text='Sets the prefix used for Rogue Trader chat commands (e.g. !rt_u, !rt_a).')
            add_switch('Overwrite Existing', 'overwrite_existing', cfg.get('overwrite_existing', False), hover_text='If enabled, the plugin will overwrite any existing commands that share the same name/prefix.')
            add_switch('Auto Install On Session', 'auto_install', cfg.get('auto_install', True), hover_text='If enabled, commands are (re)installed into user_commands.json when you start a session.')
            add_switch('Enable Help Command', 'enable_help_command', cfg.get('enable_help_command', True), hover_text='If enabled, a help command like !rt_help is added so chat can see what was installed.')

            groups = cfg.get('groups') or {}
            add_switch('Group: Movement', 'groups.movement', groups.get('movement', True), hover_text='Enable/disable movement commands (left stick: walk/strafe).')
            add_switch('Group: Camera', 'groups.camera', groups.get('camera', True), hover_text='Enable/disable camera commands (right stick: pan/rotate).')
            add_switch('Group: UI', 'groups.ui', groups.get('ui', True), hover_text='Enable/disable UI interaction commands (A/B/X/Y, D-pad, menu).')
            add_switch('Group: Combat', 'groups.combat', groups.get('combat', True), hover_text='Enable/disable combat helper commands (end turn, rotate/zoom, target cycling).')
            add_switch('Group: Safety', 'groups.safety', groups.get('safety', True), hover_text='Enable/disable safety commands (pausing/binding toggles).')

            d = cfg.get('defaults') or {}
            add_text('Default Move Hold (sec)', 'defaults.move_hold', d.get('move_hold', 0.8), hover_text='Default duration used by the short movement commands (e.g. !rt_u).')
            add_text('Default Camera Hold (sec)', 'defaults.cam_hold', d.get('cam_hold', 0.4), hover_text='Default duration used by the short camera commands (e.g. !rt_cu1).')
            add_text('Default Tap Hold (sec)', 'defaults.tap_hold', d.get('tap_hold', 0.2), hover_text='Default duration used for quick button taps (e.g. !rt_a1).')

            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
            row.add_widget(Label(text='Command Mappings', size_hint_x=0.70))
            reset_btn = Button(text='Reset to Defaults', size_hint_x=0.30)
            row.add_widget(reset_btn)
            self._bindings_container.add_widget(row)

            def _reset(_btn):
                self._rt_reset_to_defaults = True
                self._active_bindings_kind = 'plugin:games.rogue_trader'
                self._render_plugin_bindings('games.rogue_trader')

            reset_btn.bind(on_press=_reset)

            cmds = cfg.get('custom_commands')
            if self._rt_reset_to_defaults:
                cmds = self._get_rogue_trader_default_commands()
            if not isinstance(cmds, dict) or not cmds:
                cmds = self._get_rogue_trader_default_commands()

            labels = cfg.get('custom_command_labels')
            default_labels = self._get_rogue_trader_default_labels()
            if self._rt_reset_to_defaults:
                labels = dict(default_labels)
            else:
                if not isinstance(labels, dict) or labels is None:
                    labels = {}
                merged = dict(default_labels)
                merged.update(labels)
                labels = merged

            mappings = GridLayout(cols=1, size_hint_y=None)
            mappings.bind(minimum_height=mappings.setter('height'))

            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
            header.add_widget(Label(text='Chat Command', size_hint_x=0.32))
            header.add_widget(Label(text='Internal Command', size_hint_x=0.43))
            header.add_widget(Label(text='Label', size_hint_x=0.20))
            header.add_widget(Label(text='', size_hint_x=0.05))
            mappings.add_widget(header)

            def add_row(k, v, lbl_text):
                r = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
                k_in = TextInput(text=str(k), multiline=False, size_hint_x=0.32)
                v_in = TextInput(text=str(v), multiline=False, size_hint_x=0.43)
                l_in = TextInput(text=str(lbl_text), multiline=False, size_hint_x=0.20)
                rm = Button(text='X', size_hint_x=0.05)
                r.add_widget(k_in)
                r.add_widget(v_in)
                r.add_widget(l_in)
                r.add_widget(rm)
                mappings.add_widget(r)
                self._rt_command_rows.append((k_in, v_in, l_in, r, mappings))

                def _rm(*_):
                    try:
                        mappings.remove_widget(r)
                    except Exception:
                        pass
                    try:
                        self._rt_command_rows = [t for t in self._rt_command_rows if t[2] is not r]
                    except Exception:
                        pass

                rm.bind(on_press=_rm)

            for k in sorted(cmds.keys()):
                add_row(k, cmds.get(k), labels.get(k, ''))

            add_btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
            add_btn_row.add_widget(Label(text='', size_hint_x=0.70))
            add_btn = Button(text='Add Mapping', size_hint_x=0.30)
            add_btn_row.add_widget(add_btn)
            mappings.add_widget(add_btn_row)

            def _add(_btn):
                add_row('', '', '')

            add_btn.bind(on_press=_add)

            sv2 = ScrollView(do_scroll_x=False)
            sv2.add_widget(mappings)
            self._bindings_container.add_widget(sv2)
        else:
            add_text('Plugin Config (JSON) path', 'info', plugin_manager.api.get_plugin_config_path(plugin_id),)

        sv = ScrollView(do_scroll_x=False)
        sv.add_widget(grid)
        self._bindings_container.add_widget(sv)

    def _add_binding_row(self, alias, value, parent=None):
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
        alias_in = TextInput(text=alias, multiline=False, size_hint_x=0.45)
        value_in = TextInput(text=value, multiline=False, size_hint_x=0.45)
        rm = Button(text='X', size_hint_x=0.10)
        row.add_widget(alias_in)
        row.add_widget(value_in)
        row.add_widget(rm)

        def _remove(*_):
            if parent is not None:
                parent.remove_widget(row)
            try:
                self._binding_rows.remove((alias_in, value_in))
            except ValueError:
                pass

        rm.bind(on_press=_remove)

        self._binding_rows.append((alias_in, value_in))

        if parent is not None:
            parent.add_widget(row)

    def _save_twitch(self):
        try:
            obj = {
                'bot_name': self._twitch_inputs.get('bot_name').text,
                'bot_oAuth': self._twitch_inputs.get('bot_oAuth').text,
                'streamer_name': self._twitch_inputs.get('streamer_name').text,
            }
            self._write_json('login', obj)
            self._set_status('Saved Twitch settings')
        except Exception as e:
            self._set_status('Save failed: {}'.format(e))

    def _save_plugin_bindings(self, plugin_id: str):
        plugin_manager = getattr(self.parent, 'plugin_manager', None)
        if plugin_manager is None:
            self._set_status('Plugin manager not available')
            return

        defaults = None
        if plugin_id == 'games.rogue_trader':
            defaults = self._get_rogue_trader_default_config()
        else:
            defaults = {}

        try:
            cfg = plugin_manager.api.load_plugin_config(plugin_id=plugin_id, default=defaults)
        except Exception:
            cfg = dict(defaults or {})

        try:
            if plugin_id == 'games.rogue_trader':
                prefix = self._plugin_binding_inputs.get('prefix')
                overwrite = self._plugin_binding_inputs.get('overwrite_existing')
                auto_install = self._plugin_binding_inputs.get('auto_install')
                help_cmd = self._plugin_binding_inputs.get('enable_help_command')

                if prefix is not None:
                    cfg['prefix'] = str(getattr(prefix, 'text', '')).strip() or 'rt'
                if overwrite is not None:
                    cfg['overwrite_existing'] = bool(getattr(overwrite, 'active', False))
                if auto_install is not None:
                    cfg['auto_install'] = bool(getattr(auto_install, 'active', True))
                if help_cmd is not None:
                    cfg['enable_help_command'] = bool(getattr(help_cmd, 'active', True))

                groups = cfg.get('groups') or {}
                for k in ['movement', 'camera', 'ui', 'combat', 'safety']:
                    sw = self._plugin_binding_inputs.get('groups.' + k)
                    if sw is not None:
                        groups[k] = bool(getattr(sw, 'active', True))
                cfg['groups'] = groups

                d = cfg.get('defaults') or {}
                for k in ['move_hold', 'cam_hold', 'tap_hold']:
                    ti = self._plugin_binding_inputs.get('defaults.' + k)
                    if ti is not None:
                        d[k] = self._parse_value(getattr(ti, 'text', ''))
                cfg['defaults'] = d

                custom = {}
                custom_labels = {}
                for k_in, v_in, l_in, _row, _parent in list(self._rt_command_rows):
                    k = str(getattr(k_in, 'text', '')).strip()
                    v = str(getattr(v_in, 'text', '')).strip()
                    lbl = str(getattr(l_in, 'text', '')).strip()
                    if not k or not v:
                        continue
                    custom[k] = v
                    if lbl:
                        custom_labels[k] = lbl

                if self._rt_reset_to_defaults:
                    cfg['custom_commands'] = self._get_rogue_trader_default_commands()
                    cfg['custom_command_labels'] = self._get_rogue_trader_default_labels()
                    self._rt_reset_to_defaults = False
                else:
                    cfg['custom_commands'] = custom
                    cfg['custom_command_labels'] = custom_labels

            plugin_manager.api.save_plugin_config(cfg, plugin_id=plugin_id)
            self._set_status('Saved plugin bindings: {}'.format(plugin_id))
        except Exception as e:
            self._set_status('Save failed: {}'.format(e))

    def _save_emulator(self):
        try:
            obj = {
                'emu_path': self._emu_inputs.get('emu_path').text,
                'process_name': self._emu_inputs.get('process_name').text,
                'pid': bool(self._emu_inputs.get('pid').active),
            }
            self._write_json('emulator_settings', obj)
            self._set_status('Saved emulator settings')
        except Exception as e:
            self._set_status('Save failed: {}'.format(e))

    def _parse_value(self, s):
        t = str(s).strip()
        if t.lower() == 'true':
            return True
        if t.lower() == 'false':
            return False
        try:
            if '.' in t:
                return float(t)
            return int(t)
        except Exception:
            return t

    def _save_bindings(self):
        key = self._active_bindings_kind
        if str(key).startswith('plugin:'):
            self._save_plugin_bindings(str(key).split(':', 1)[1])
            return
        try:
            out = {}
            if key == 'aliases_axes' and self._axes_comment is not None:
                out['_comment'] = self._axes_comment

            for alias_in, value_in in list(self._binding_rows):
                k = alias_in.text.strip()
                if not k:
                    continue
                out[k] = self._parse_value(value_in.text)

            self._write_json(key, out)
            self._set_status('Saved bindings: {}'.format(key))
        except Exception as e:
            self._set_status('Save failed: {}'.format(e))
