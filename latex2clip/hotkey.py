"""Global hotkey via Carbon RegisterEventHotKey.

This is the standard macOS mechanism for system-wide hotkeys.
Used by Alfred, Raycast, Spotlight, etc.
Does NOT require Accessibility or Input Monitoring permission.
"""

from __future__ import annotations

import ctypes
import ctypes.util
from ctypes import byref, c_uint32, c_void_p, Structure, CFUNCTYPE
from typing import Callable

import AppKit

# ---- Load Carbon framework ----
_carbon_path = ctypes.util.find_library("Carbon")
_carbon = ctypes.cdll.LoadLibrary(_carbon_path)

# ---- Carbon types ----
class _EventHotKeyID(Structure):
    _fields_ = [("signature", c_uint32), ("id", c_uint32)]

# ---- Carbon modifier constants ----
_CARBON_MODS = {
    "cmd":   0x0100,   # cmdKey
    "shift": 0x0200,   # shiftKey
    "alt":   0x0800,   # optionKey
    "ctrl":  0x1000,   # controlKey
}

# ---- Virtual keycodes (same as CGEvent) ----
KEY_CODES: dict[str, int] = {
    "A": 0x00, "S": 0x01, "D": 0x02, "F": 0x03,
    "H": 0x04, "G": 0x05, "Z": 0x06, "X": 0x07,
    "C": 0x08, "V": 0x09, "B": 0x0B, "Q": 0x0C,
    "W": 0x0D, "E": 0x0E, "R": 0x0F, "Y": 0x10,
    "T": 0x11, "1": 0x12, "2": 0x13, "3": 0x14,
    "4": 0x15, "6": 0x16, "5": 0x17, "9": 0x19,
    "7": 0x1A, "8": 0x1C, "0": 0x1D, "L": 0x25,
    "M": 0x2E, "N": 0x2D, "O": 0x1F, "P": 0x23,
    "I": 0x22, "U": 0x20, "J": 0x26, "K": 0x28,
}

# For NSEvent modifier flags (used by recording)
MODIFIERS: dict[str, int] = {
    "cmd": AppKit.NSEventModifierFlagCommand,
    "ctrl": AppKit.NSEventModifierFlagControl,
    "alt": AppKit.NSEventModifierFlagOption,
    "shift": AppKit.NSEventModifierFlagShift,
}

_ALL_MOD_MASK = (
    AppKit.NSEventModifierFlagCommand
    | AppKit.NSEventModifierFlagControl
    | AppKit.NSEventModifierFlagOption
    | AppKit.NSEventModifierFlagShift
)

_CODE_TO_KEY = {v: k for k, v in KEY_CODES.items()}

# ---- Carbon event handler type ----
# OSStatus (*EventHandlerProcPtr)(EventHandlerCallRef, EventRef, void*)
_EventHandlerProcPtr = CFUNCTYPE(c_uint32, c_void_p, c_void_p, c_void_p)

# ---- Carbon event constants ----
_kEventClassKeyboard = 0x6B657962  # 'keyb' as uint32
_kEventHotKeyPressed = 5

class _EventTypeSpec(Structure):
    _fields_ = [("eventClass", c_uint32), ("eventKind", c_uint32)]

# ---- Carbon API functions ----
_carbon.GetApplicationEventTarget.restype = c_void_p
_carbon.InstallEventHandler.argtypes = [
    c_void_p, _EventHandlerProcPtr, c_uint32,
    ctypes.POINTER(_EventTypeSpec), c_void_p, c_void_p
]
_carbon.InstallEventHandler.restype = c_uint32  # OSStatus
_carbon.RegisterEventHotKey.argtypes = [
    c_uint32, c_uint32, _EventHotKeyID, c_void_p, c_uint32, c_void_p
]
_carbon.RegisterEventHotKey.restype = c_uint32
_carbon.UnregisterEventHotKey.argtypes = [c_void_p]
_carbon.UnregisterEventHotKey.restype = c_uint32


class HotkeyListener:
    """System-wide hotkey using Carbon RegisterEventHotKey (no permissions needed)."""

    def __init__(self, key: str, modifiers: list[str], callback: Callable[[], None]) -> None:
        self.callback = callback
        self._hotkey_ref = c_void_p()
        self._handler_ref = c_void_p()
        self._handler_proc = None  # prevent GC
        self._target_key = key.upper()
        self._target_mods = [m.lower() for m in modifiers]

    def start(self) -> None:
        # Install Carbon event handler
        self._handler_proc = _EventHandlerProcPtr(self._carbon_handler)
        event_type = _EventTypeSpec(_kEventClassKeyboard, _kEventHotKeyPressed)

        status = _carbon.InstallEventHandler(
            _carbon.GetApplicationEventTarget(),
            self._handler_proc,
            1,
            byref(event_type),
            None,
            byref(self._handler_ref),
        )
        if status != 0:
            raise RuntimeError(f"InstallEventHandler failed: {status}")

        self._register_key()
        print(f"[Texmail] Carbon hotkey registered: {'+'.join(self._target_mods)}+{self._target_key}")

    def _register_key(self) -> None:
        # Unregister old key if any
        if self._hotkey_ref.value:
            _carbon.UnregisterEventHotKey(self._hotkey_ref)
            self._hotkey_ref = c_void_p()

        keycode = KEY_CODES.get(self._target_key)
        if keycode is None:
            raise ValueError(f"Unknown key: {self._target_key}")

        carbon_mods = 0
        for m in self._target_mods:
            if m not in _CARBON_MODS:
                raise ValueError(f"Unknown modifier: {m}")
            carbon_mods |= _CARBON_MODS[m]

        hotkey_id = _EventHotKeyID(signature=0x4C325843, id=1)  # 'L2XC'

        status = _carbon.RegisterEventHotKey(
            c_uint32(keycode),
            c_uint32(carbon_mods),
            hotkey_id,
            _carbon.GetApplicationEventTarget(),
            c_uint32(0),
            byref(self._hotkey_ref),
        )
        if status != 0:
            raise RuntimeError(f"RegisterEventHotKey failed: {status}")

    def _carbon_handler(self, handler_call_ref, event_ref, user_data):
        """Called by Carbon when hotkey is pressed."""
        self.callback()
        return 0  # noErr

    def update_hotkey(self, key: str, modifiers: list[str]) -> None:
        self._target_key = key.upper()
        self._target_mods = [m.lower() for m in modifiers]
        self._register_key()
        print(f"[Texmail] Hotkey updated: {'+'.join(self._target_mods)}+{self._target_key}")

    def stop(self) -> None:
        if self._hotkey_ref.value:
            _carbon.UnregisterEventHotKey(self._hotkey_ref)
