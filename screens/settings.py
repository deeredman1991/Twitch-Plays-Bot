import os
import io
import json
import time

from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
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
        self.make_button(nav, 'Twitch', lambda *a: self.show_page('twitch'), sx=0.33, sy=1)
        self.make_button(nav, 'Emulator', lambda *a: self.show_page('emulator'), sx=0.33, sy=1)
        self.make_button(nav, 'Bindings', lambda *a: self.show_page('bindings'), sx=0.34, sy=1)

        status_row = self.make_box(root, o='horizontal', sy=0.08)
        self._status_label = Label(text='')
        status_row.add_widget(self._status_label)

        self._content_holder = self.make_box(root, sy=0.70)

        bottom = self.make_box(root, o='horizontal', sy=0.10)
        self.make_button(bottom, 'Reload', lambda *a: self.reload_from_files(), sx=0.25, sy=1)
        self.make_button(bottom, 'Save', lambda *a: self.save_active_page(), sx=0.25, sy=1)
        self.make_button(bottom, 'Back', self.back_button_on_press, sx=0.25, sy=1)
        self.make_box(bottom, sx=0.25, sy=1)

    def show_page(self, page):
        self._active_page = page

        if self._content_holder is None:
            return

        self._content_holder.clear_widgets()

        if page == 'twitch':
            self._content_holder.add_widget(self._build_twitch_page())
        elif page == 'emulator':
            self._content_holder.add_widget(self._build_emulator_page())
        else:
            self._content_holder.add_widget(self._build_bindings_page())

    def _read_json(self, key):
        path = self._file_path(key)
        with io.open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _backup_if_exists(self, path):
        if os.path.isfile(path):
            ts = time.strftime('%Y%m%d_%H%M%S')
            bak = path + '.bak_' + ts
            with io.open(path, 'r', encoding='utf-8') as src:
                prev = src.read()
            with io.open(bak, 'w', encoding='utf-8') as dst:
                dst.write(prev)

    def _write_json(self, key, obj):
        path = self._file_path(key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._backup_if_exists(path)
        with io.open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)

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
        else:
            self._save_bindings()

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
