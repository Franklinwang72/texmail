import AppKit
import SwiftUI

class ShortcutCaptureView: NSView {
    var onCapture: ((String, [String]) -> Void)?
    var onCancel: (() -> Void)?
    var isRecording = false

    override var acceptsFirstResponder: Bool { true }

    override func keyDown(with event: NSEvent) {
        guard isRecording else { return }

        let flags = event.modifierFlags.intersection(.deviceIndependentFlagsMask)

        // Need at least one modifier
        guard flags.contains(.command) || flags.contains(.shift)
           || flags.contains(.option) || flags.contains(.control) else {
            // Escape key cancels recording
            if event.keyCode == 53 { cancelRecording() }
            return
        }

        guard let keyName = codeToKey[UInt32(event.keyCode)] else {
            // Unknown key (arrow, F-key, etc.) — ignore silently but don't get stuck
            return
        }

        var mods: [String] = []
        if flags.contains(.command) { mods.append("cmd") }
        if flags.contains(.shift) { mods.append("shift") }
        if flags.contains(.option) { mods.append("alt") }
        if flags.contains(.control) { mods.append("ctrl") }

        isRecording = false
        onCapture?(keyName, mods)
    }

    override func performKeyEquivalent(with event: NSEvent) -> Bool {
        if isRecording { keyDown(with: event); return true }
        return false
    }

    // Cancel if user clicks away
    override func resignFirstResponder() -> Bool {
        if isRecording { cancelRecording() }
        return super.resignFirstResponder()
    }

    private func cancelRecording() {
        isRecording = false
        onCancel?()
    }
}

struct ShortcutRecorderRepresentable: NSViewRepresentable {
    @Binding var isRecording: Bool
    var onCapture: (String, [String]) -> Void

    func makeNSView(context: Context) -> ShortcutCaptureView {
        let view = ShortcutCaptureView()
        view.onCapture = onCapture
        view.onCancel = { isRecording = false }
        return view
    }

    func updateNSView(_ nsView: ShortcutCaptureView, context: Context) {
        nsView.isRecording = isRecording
        nsView.onCapture = onCapture
        nsView.onCancel = { isRecording = false }
        if isRecording {
            DispatchQueue.main.async {
                nsView.window?.makeFirstResponder(nsView)
            }
        }
    }
}
