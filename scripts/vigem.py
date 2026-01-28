import os
import ctypes
from ctypes import wintypes


class ViGEmError(Exception):
    pass


VIGEM_ERROR_NONE = 0x20000000


class XUSB_REPORT(ctypes.Structure):
    _fields_ = [
        ("wButtons", wintypes.WORD),
        ("bLeftTrigger", wintypes.BYTE),
        ("bRightTrigger", wintypes.BYTE),
        ("sThumbLX", wintypes.SHORT),
        ("sThumbLY", wintypes.SHORT),
        ("sThumbRX", wintypes.SHORT),
        ("sThumbRY", wintypes.SHORT),
    ]


_XUSB_GAMEPAD_DPAD_UP = 0x0001
_XUSB_GAMEPAD_DPAD_DOWN = 0x0002
_XUSB_GAMEPAD_DPAD_LEFT = 0x0004
_XUSB_GAMEPAD_DPAD_RIGHT = 0x0008
_XUSB_GAMEPAD_START = 0x0010
_XUSB_GAMEPAD_BACK = 0x0020
_XUSB_GAMEPAD_LEFT_THUMB = 0x0040
_XUSB_GAMEPAD_RIGHT_THUMB = 0x0080
_XUSB_GAMEPAD_LEFT_SHOULDER = 0x0100
_XUSB_GAMEPAD_RIGHT_SHOULDER = 0x0200
_XUSB_GAMEPAD_GUIDE = 0x0400
_XUSB_GAMEPAD_A = 0x1000
_XUSB_GAMEPAD_B = 0x2000
_XUSB_GAMEPAD_X = 0x4000
_XUSB_GAMEPAD_Y = 0x8000


_VJOY_AXIS_X = 0x30
_VJOY_AXIS_Y = 0x31
_VJOY_AXIS_Z = 0x32
_VJOY_AXIS_RX = 0x33
_VJOY_AXIS_RY = 0x34
_VJOY_AXIS_RZ = 0x35
_VJOY_AXIS_SL0 = 0x36
_VJOY_AXIS_SL1 = 0x37


def _find_vigemclient_dll():
    env_path = os.environ.get("VIGEMCLIENT_DLL")
    if env_path and os.path.isfile(env_path):
        return env_path

    candidates = [
        os.path.join(os.path.dirname(__file__), "ViGEmClient.dll"),
        os.path.join(os.getcwd(), "ViGEmClient.dll"),
    ]

    path_env = os.environ.get("PATH", "")
    for p in path_env.split(os.pathsep):
        p = p.strip('"')
        if not p:
            continue
        candidates.append(os.path.join(p, "ViGEmClient.dll"))

    for c in candidates:
        if os.path.isfile(c):
            return c

    return None


def _to_short_from_vjoy_axis_value(vjoy_value):
    v = int(vjoy_value)
    if v < 0:
        v = 0
    if v > 0x8000:
        v = 0x8000
    signed = int(round((v - 0x4000) * 32768.0 / 0x4000))
    if signed < -32768:
        signed = -32768
    if signed > 32767:
        signed = 32767
    return signed


class _ViGEmBackend(object):
    def __init__(self):
        self._dll = None
        self._client = None
        self._controllers = {}

    def _load(self):
        if self._dll is not None:
            return

        dll_path = _find_vigemclient_dll()
        if not dll_path:
            raise ViGEmError(
                "Unable to load ViGEmClient.dll. Place ViGEmClient.dll next to scripts/vigem.py "
                "or set VIGEMCLIENT_DLL to its full path."
            )

        self._dll = ctypes.CDLL(dll_path)

        self._dll.vigem_alloc.restype = ctypes.c_void_p

        self._dll.vigem_connect.argtypes = [ctypes.c_void_p]
        self._dll.vigem_connect.restype = wintypes.ULONG

        self._dll.vigem_disconnect.argtypes = [ctypes.c_void_p]
        self._dll.vigem_disconnect.restype = None

        self._dll.vigem_free.argtypes = [ctypes.c_void_p]
        self._dll.vigem_free.restype = None

        self._dll.vigem_target_x360_alloc.restype = ctypes.c_void_p

        self._dll.vigem_target_add.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self._dll.vigem_target_add.restype = wintypes.ULONG

        self._dll.vigem_target_remove.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self._dll.vigem_target_remove.restype = wintypes.ULONG

        self._dll.vigem_target_free.argtypes = [ctypes.c_void_p]
        self._dll.vigem_target_free.restype = None

        self._dll.vigem_target_x360_update.argtypes = [ctypes.c_void_p, ctypes.c_void_p, XUSB_REPORT]
        self._dll.vigem_target_x360_update.restype = wintypes.ULONG

    def _ensure_client(self):
        self._load()
        if self._client is not None:
            return
        self._client = self._dll.vigem_alloc()
        if not self._client:
            raise ViGEmError("vigem_alloc returned NULL")
        err = self._dll.vigem_connect(self._client)
        if err != VIGEM_ERROR_NONE:
            raise ViGEmError("vigem_connect failed with error code {}".format(err))

    def _ensure_controller(self, rID):
        self._ensure_client()

        rid = int(rID)
        if rid in self._controllers:
            return

        target = self._dll.vigem_target_x360_alloc()
        if not target:
            raise ViGEmError("vigem_target_x360_alloc returned NULL")

        err = self._dll.vigem_target_add(self._client, target)
        if err != VIGEM_ERROR_NONE:
            self._dll.vigem_target_free(target)
            raise ViGEmError("vigem_target_add failed with error code {}".format(err))

        report = XUSB_REPORT()
        report.wButtons = 0
        report.bLeftTrigger = 0
        report.bRightTrigger = 0
        report.sThumbLX = 0
        report.sThumbLY = 0
        report.sThumbRX = 0
        report.sThumbRY = 0

        self._controllers[rid] = {"target": target, "report": report}
        self._update(rid)

    def _update(self, rID):
        rid = int(rID)
        c = self._controllers.get(rid)
        if not c:
            return
        err = self._dll.vigem_target_x360_update(self._client, c["target"], c["report"])
        if err != VIGEM_ERROR_NONE:
            raise ViGEmError("vigem_target_x360_update failed with error code {}".format(err))

    def acquire(self, rID):
        self._ensure_controller(rID)
        return True

    def set_button(self, state, rID, button_id):
        self._ensure_controller(rID)
        rid = int(rID)
        c = self._controllers[rid]
        report = c["report"]

        pressed = bool(int(state))
        bid = int(button_id)

        if bid == 1:
            mask = _XUSB_GAMEPAD_A
        elif bid == 2:
            mask = _XUSB_GAMEPAD_B
        elif bid == 3:
            mask = _XUSB_GAMEPAD_X
        elif bid == 4:
            mask = _XUSB_GAMEPAD_Y
        elif bid == 5:
            mask = _XUSB_GAMEPAD_RIGHT_SHOULDER
        elif bid == 6:
            mask = _XUSB_GAMEPAD_LEFT_SHOULDER
        elif bid == 9:
            mask = _XUSB_GAMEPAD_LEFT_THUMB
        elif bid == 10:
            mask = _XUSB_GAMEPAD_RIGHT_THUMB
        elif bid == 11:
            mask = _XUSB_GAMEPAD_START
        elif bid == 12:
            mask = _XUSB_GAMEPAD_BACK
        elif bid == 7:
            report.bRightTrigger = 255 if pressed else 0
            self._update(rid)
            return
        elif bid == 8:
            report.bLeftTrigger = 255 if pressed else 0
            self._update(rid)
            return
        else:
            return

        if pressed:
            report.wButtons = wintypes.WORD(report.wButtons | mask)
        else:
            report.wButtons = wintypes.WORD(report.wButtons & (~mask & 0xFFFF))

        self._update(rid)

    def set_axis(self, value, rID, axis_id):
        self._ensure_controller(rID)
        rid = int(rID)
        c = self._controllers[rid]
        report = c["report"]

        a = int(axis_id)
        v = _to_short_from_vjoy_axis_value(value)

        if a == _VJOY_AXIS_X:
            report.sThumbLX = v
        elif a == _VJOY_AXIS_Y:
            report.sThumbLY = v
        elif a == _VJOY_AXIS_Z:
            report.sThumbRX = v
        elif a == _VJOY_AXIS_RX:
            report.sThumbRY = v
        elif a == _VJOY_AXIS_RY:
            report.sThumbRX = v
        elif a == _VJOY_AXIS_RZ:
            report.sThumbRY = v
        elif a == _VJOY_AXIS_SL0:
            report.sThumbLX = v
        elif a == _VJOY_AXIS_SL1:
            report.sThumbLY = v
        else:
            return

        self._update(rid)

    def set_cont_pov(self, value, rID, hat_id):
        self._ensure_controller(rID)
        rid = int(rID)
        c = self._controllers.get(rid)
        report = c["report"]

        hid = int(hat_id)
        if hid != 1:
            return

        report.wButtons = wintypes.WORD(report.wButtons & (~(_XUSB_GAMEPAD_DPAD_UP | _XUSB_GAMEPAD_DPAD_DOWN | _XUSB_GAMEPAD_DPAD_LEFT | _XUSB_GAMEPAD_DPAD_RIGHT) & 0xFFFF))

        v = int(value)
        if v < 0 or v >= 36000:
            self._update(rid)
            return

        angle = v % 36000

        if angle == 0:
            report.wButtons = wintypes.WORD(report.wButtons | _XUSB_GAMEPAD_DPAD_UP)
        elif angle == 4500:
            report.wButtons = wintypes.WORD(report.wButtons | _XUSB_GAMEPAD_DPAD_UP | _XUSB_GAMEPAD_DPAD_RIGHT)
        elif angle == 9000:
            report.wButtons = wintypes.WORD(report.wButtons | _XUSB_GAMEPAD_DPAD_RIGHT)
        elif angle == 13500:
            report.wButtons = wintypes.WORD(report.wButtons | _XUSB_GAMEPAD_DPAD_DOWN | _XUSB_GAMEPAD_DPAD_RIGHT)
        elif angle == 18000:
            report.wButtons = wintypes.WORD(report.wButtons | _XUSB_GAMEPAD_DPAD_DOWN)
        elif angle == 22500:
            report.wButtons = wintypes.WORD(report.wButtons | _XUSB_GAMEPAD_DPAD_DOWN | _XUSB_GAMEPAD_DPAD_LEFT)
        elif angle == 27000:
            report.wButtons = wintypes.WORD(report.wButtons | _XUSB_GAMEPAD_DPAD_LEFT)
        elif angle == 31500:
            report.wButtons = wintypes.WORD(report.wButtons | _XUSB_GAMEPAD_DPAD_UP | _XUSB_GAMEPAD_DPAD_LEFT)

        self._update(rid)


_backend = _ViGEmBackend()


class _VJoyShim(object):
    def AcquireVJD(self, rID):
        return _backend.acquire(rID)

    def SetBtn(self, state, rID, button_id):
        return _backend.set_button(state, rID, button_id)

    def SetAxis(self, value, rID, axis_id):
        return _backend.set_axis(value, rID, axis_id)

    def SetContPov(self, value, rID, hat_id):
        return _backend.set_cont_pov(value, rID, hat_id)


vJoy = _VJoyShim()
