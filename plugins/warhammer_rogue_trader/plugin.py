from scripts.plugin_system import PluginBase


class Plugin(PluginBase):
    plugin_id = 'games.rogue_trader'
    name = 'WH40K: Rogue Trader Command Pack'
    version = '1.0.0'

    def on_load(self, api):
        self.api = api
        api.subscribe('session_started', self._on_session_started)
        print('[RogueTraderPlugin] loaded (waiting for session_started)')

    def _on_session_started(self, commands_manager=None, profile=None, **payload):
        print(f"[RogueTraderPlugin] session_started received profile={profile} commands_manager={type(commands_manager)}")
        if commands_manager is None:
            return

        cfg = self.api.load_plugin_config(default={
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
        })

        if not cfg.get('enabled', True):
            return
        if not cfg.get('auto_install', True):
            return

        prefix = str(cfg.get('prefix', 'rt')).strip()
        if not prefix:
            prefix = 'rt'

        overwrite = bool(cfg.get('overwrite_existing', False))

        groups = cfg.get('groups') or {}
        enable_movement = bool(groups.get('movement', True))
        enable_camera = bool(groups.get('camera', True))
        enable_ui = bool(groups.get('ui', True))
        enable_combat = bool(groups.get('combat', True))
        enable_safety = bool(groups.get('safety', True))

        defaults = cfg.get('defaults') or {}
        move_hold = defaults.get('move_hold', 0.8)
        cam_hold = defaults.get('cam_hold', 0.4)
        tap_hold = defaults.get('tap_hold', 0.2)

        # Notes:
        # - This bot backend is gamepad/vJoy oriented. These commands assume you are playing Rogue Trader with controller input.
        # - We only add commands; we do not remove existing ones.
        # - All commands are prefixed to avoid collisions with your global command set.

        custom_commands = cfg.get('custom_commands')
        cmd = None
        if isinstance(custom_commands, dict) and custom_commands:
            out = {}
            for k, v in custom_commands.items():
                try:
                    kk = str(k)
                    vv = str(v)
                except Exception:
                    continue
                if '{p}' in kk:
                    kk = kk.replace('{p}', prefix)
                out[kk] = vv
            cmd = out
        else:
            cmd = self._build_command_pack(
                prefix,
                move_hold=move_hold,
                cam_hold=cam_hold,
                tap_hold=tap_hold,
                enable_movement=enable_movement,
                enable_camera=enable_camera,
                enable_ui=enable_ui,
                enable_combat=enable_combat,
                enable_safety=enable_safety,
            )

        installed = 0
        skipped = 0

        existing = {}
        try:
            existing = commands_manager.configs.get('user_commands', {}) or {}
        except Exception:
            existing = {}

        for k, v in cmd.items():
            if (k in existing) and (not overwrite):
                skipped += 1
                continue
            commands_manager.set_config('user_commands', k, v)
            installed += 1

        if cfg.get('enable_help_command', True):
            help_key = f"!{prefix}_help"
            help_value = (
                ":send Rogue Trader controls installed. Try !{p}_wu/!{p}_wd/!{p}_wl/!{p}_wr, !{p}_cu/!{p}_cd/!{p}_cl/!{p}_cr, !{p}_a/!{p}_b."
            ).format(p=prefix)
            if (help_key not in existing) or overwrite:
                commands_manager.set_config('user_commands', help_key, help_value)

        print(f"[RogueTraderPlugin] profile={profile} installed={installed} skipped={skipped} overwrite={overwrite}")

    def _build_command_pack(
        self,
        prefix: str,
        *,
        move_hold=0.8,
        cam_hold=0.4,
        tap_hold=0.2,
        enable_movement=True,
        enable_camera=True,
        enable_ui=True,
        enable_combat=True,
        enable_safety=True,
    ):
        p = prefix

        # Movement uses left stick (lx/ly). Camera uses right stick (rx/ry).
        # Buttons:
        # - x/o/s/t map to controller face buttons via aliases_buttons.json.
        # - l1/r1/l2/r2/l3/r3 are also available.
        # - st/se are start/select.
        # Dpad uses :hat 1 <dir>.

        cmds = {}

        if enable_movement:
            cmds.update({
                # --- Movement (left stick) ---
                f"!{p}_move_up #(hold_for=0.2:3)": ":tilt lx fd #(hold_for) smooth",
                f"!{p}_move_down #(hold_for=0.2:3)": ":tilt lx bk #(hold_for) smooth",
                f"!{p}_move_left #(hold_for=0.2:3)": ":tilt ly lf #(hold_for) smooth",
                f"!{p}_move_right #(hold_for=0.2:3)": ":tilt ly ri #(hold_for) smooth",

                # Short aliases
                f"!{p}_wu #(hold_for=0.2:3)": ":tilt lx fd #(hold_for) smooth",
                f"!{p}_wd #(hold_for=0.2:3)": ":tilt lx bk #(hold_for) smooth",
                f"!{p}_wl #(hold_for=0.2:3)": ":tilt ly lf #(hold_for) smooth",
                f"!{p}_wr #(hold_for=0.2:3)": ":tilt ly ri #(hold_for) smooth",

                # Default-timed versions
                f"!{p}_u": f":tilt lx fd {move_hold} smooth",
                f"!{p}_d": f":tilt lx bk {move_hold} smooth",
                f"!{p}_l": f":tilt ly lf {move_hold} smooth",
                f"!{p}_r": f":tilt ly ri {move_hold} smooth",
            })

        if enable_camera:
            cmds.update({
                # --- Camera (right stick) ---
                f"!{p}_cam_up #(hold_for=0.1:2)": ":tilt rx fd #(hold_for) choppy",
                f"!{p}_cam_down #(hold_for=0.1:2)": ":tilt rx bk #(hold_for) choppy",
                f"!{p}_cam_left #(hold_for=0.1:2)": ":tilt ry lf #(hold_for) choppy",
                f"!{p}_cam_right #(hold_for=0.1:2)": ":tilt ry ri #(hold_for) choppy",

                # Short aliases
                f"!{p}_cu #(hold_for=0.1:2)": ":tilt rx fd #(hold_for) choppy",
                f"!{p}_cd #(hold_for=0.1:2)": ":tilt rx bk #(hold_for) choppy",
                f"!{p}_cl #(hold_for=0.1:2)": ":tilt ry lf #(hold_for) choppy",
                f"!{p}_cr #(hold_for=0.1:2)": ":tilt ry ri #(hold_for) choppy",

                # Default-timed versions
                f"!{p}_cu1": f":tilt rx fd {cam_hold} choppy",
                f"!{p}_cd1": f":tilt rx bk {cam_hold} choppy",
                f"!{p}_cl1": f":tilt ry lf {cam_hold} choppy",
                f"!{p}_cr1": f":tilt ry ri {cam_hold} choppy",
            })

        if enable_ui:
            cmds.update({
                # --- Confirm/Cancel and common actions ---
                f"!{p}_a #(hold_for=0.1:1)": ":mash x 1 0.1 #(hold_for)",
                f"!{p}_b #(hold_for=0.1:1)": ":mash o 1 0.1 #(hold_for)",
                f"!{p}_x #(hold_for=0.1:1)": ":mash s 1 0.1 #(hold_for)",
                f"!{p}_y #(hold_for=0.1:1)": ":mash t 1 0.1 #(hold_for)",

                # Default-timed taps
                f"!{p}_a1": f":mash x 1 0.1 {tap_hold}",
                f"!{p}_b1": f":mash o 1 0.1 {tap_hold}",
                f"!{p}_x1": f":mash s 1 0.1 {tap_hold}",
                f"!{p}_y1": f":mash t 1 0.1 {tap_hold}",

                # --- D-pad navigation ---
                f"!{p}_up #(hold_for=0.1:1)": ":hat 1 up 1 0.1 #(hold_for)",
                f"!{p}_down #(hold_for=0.1:1)": ":hat 1 dn 1 0.1 #(hold_for)",
                f"!{p}_left #(hold_for=0.1:1)": ":hat 1 lf 1 0.1 #(hold_for)",
                f"!{p}_right #(hold_for=0.1:1)": ":hat 1 ri 1 0.1 #(hold_for)",

                # Menu / pause-ish
                f"!{p}_menu": ":mash se 1 0.1 0.3",
                f"!{p}_pause": ":mash se 1 0.1 0.3",
            })

        if enable_combat:
            cmds.update({
                # --- Turn / tactical helpers (best-effort mapping; customize in-game if needed) ---
                f"!{p}_end": ":mash st 1 0.1 0.3",
                f"!{p}_endturn": ":mash st 1 0.1 0.3",

                # Camera rotate / zoom (often bumpers/triggers)
                f"!{p}_rot_l #(hold_for=0.1:1)": ":mash l1 1 0.1 #(hold_for)",
                f"!{p}_rot_r #(hold_for=0.1:1)": ":mash r1 1 0.1 #(hold_for)",
                f"!{p}_zoom_in #(hold_for=0.1:1)": ":mash r2 1 0.1 #(hold_for)",
                f"!{p}_zoom_out #(hold_for=0.1:1)": ":mash l2 1 0.1 #(hold_for)",

                # Cycle targets/units (placeholders)
                f"!{p}_next #(hold_for=0.1:1)": ":mash r3 1 0.1 #(hold_for)",
                f"!{p}_prev #(hold_for=0.1:1)": ":mash l3 1 0.1 #(hold_for)",
            })

        if enable_safety:
            cmds.update({
                # These match your global bot behavior but are namespaced.
                f"!{p}_pon": ":set pausing 1",
                f"!{p}_poff": ":set pausing 0",
                f"!{p}_bindon": ":set binding 1",
                f"!{p}_bindoff": ":set binding 0",
            })

        return cmds
