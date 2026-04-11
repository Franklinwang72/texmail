import Carbon
import Foundation

// Virtual keycodes (same as macOS CGEvent keycodes)
let keyCodes: [String: UInt32] = [
    "A": 0x00, "S": 0x01, "D": 0x02, "F": 0x03,
    "H": 0x04, "G": 0x05, "Z": 0x06, "X": 0x07,
    "C": 0x08, "V": 0x09, "B": 0x0B, "Q": 0x0C,
    "W": 0x0D, "E": 0x0E, "R": 0x0F, "Y": 0x10,
    "T": 0x11, "1": 0x12, "2": 0x13, "3": 0x14,
    "4": 0x15, "6": 0x16, "5": 0x17, "9": 0x19,
    "7": 0x1A, "8": 0x1C, "0": 0x1D, "L": 0x25,
    "M": 0x2E, "N": 0x2D, "O": 0x1F, "P": 0x23,
    "I": 0x22, "U": 0x20, "J": 0x26, "K": 0x28,
]

let codeToKey: [UInt32: String] = {
    var m: [UInt32: String] = [:]
    for (k, v) in keyCodes { m[v] = k }
    return m
}()

// Carbon modifier constants
let carbonMods: [String: UInt32] = [
    "cmd":   UInt32(cmdKey),
    "shift": UInt32(shiftKey),
    "alt":   UInt32(optionKey),
    "ctrl":  UInt32(controlKey),
]

// Pointer to the singleton for the C callback
private var _sharedManager: HotkeyManager?

class HotkeyManager {
    private var handlerRef: EventHandlerRef?
    private var hotkeyRef: EventHotKeyRef?
    var action: (() -> Void)?

    init() {
        _sharedManager = self
    }

    func register(key: String, modifiers: [String], action: @escaping () -> Void) {
        self.action = action
        installHandler()
        registerKey(key: key, modifiers: modifiers)
    }

    private func installHandler() {
        var eventType = EventTypeSpec(
            eventClass: OSType(kEventClassKeyboard),
            eventKind: UInt32(kEventHotKeyPressed)
        )

        let status = InstallEventHandler(
            GetApplicationEventTarget(),
            { (_: EventHandlerCallRef?, _: EventRef?, _: UnsafeMutableRawPointer?) -> OSStatus in
                _sharedManager?.action?()
                return noErr
            },
            1,
            &eventType,
            nil,
            &handlerRef
        )

        if status != noErr {
            print("[Taxmail] InstallEventHandler failed: \(status)")
        }
    }

    func registerKey(key: String, modifiers: [String]) {
        // Unregister old key
        if let ref = hotkeyRef {
            UnregisterEventHotKey(ref)
            hotkeyRef = nil
        }

        guard let keycode = keyCodes[key.uppercased()] else {
            print("[Taxmail] Unknown key: \(key)")
            return
        }

        var carbonMask: UInt32 = 0
        for mod in modifiers {
            if let m = carbonMods[mod.lowercased()] {
                carbonMask |= m
            }
        }

        var hotKeyID = EventHotKeyID(signature: 0x4C32_5843, id: 1) // 'L2XC'
        var ref: EventHotKeyRef?

        let status = RegisterEventHotKey(
            keycode,
            carbonMask,
            hotKeyID,
            GetApplicationEventTarget(),
            0,
            &ref
        )

        if status == noErr {
            hotkeyRef = ref
            let display = modifiers.map { modSymbols[$0] ?? $0 }.joined() + key.uppercased()
            print("[Taxmail] Hotkey registered: \(display) (keycode=\(keycode), mods=\(carbonMask))", terminator: "\n")
        } else {
            print("[Taxmail] RegisterEventHotKey FAILED: status=\(status)", terminator: "\n")
        }
    }

    func unregister() {
        if let ref = hotkeyRef {
            UnregisterEventHotKey(ref)
            hotkeyRef = nil
        }
    }
}

// Display symbols
let modSymbols: [String: String] = [
    "cmd": "⌘", "shift": "⇧", "alt": "⌥", "ctrl": "⌃"
]

func displayShortcut(key: String, modifiers: [String]) -> String {
    modifiers.map { modSymbols[$0] ?? $0 }.joined() + key.uppercased()
}
