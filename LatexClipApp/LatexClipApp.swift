import SwiftUI
import AppKit
import ApplicationServices
import ServiceManagement

@main
struct TexmailApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    @State private var shortcutDisplay: String = "⌘⇧L"

    var body: some Scene {
        // Main settings window
        WindowGroup {
            ContentView()
        }
        .defaultSize(width: 480, height: 400)
        .windowResizability(.contentSize)

        // Menu bar icon
        MenuBarExtra("Texmail", systemImage: "sum") {
            Text("Texmail")
                .font(.headline)

            Divider()

            Button("Convert Clipboard") {
                let cfg = loadConfig()
                appDelegate.conversionService.performFullConversion(fontSize: cfg.fontSizePt) { _ in }
            }

            Text("Shortcut: \(shortcutDisplay)")
                .foregroundStyle(.secondary)

            Divider()

            Button("Settings...") {
                NSApp.activate(ignoringOtherApps: true)
            }
            .keyboardShortcut(",")

            Button(appDelegate.launchAtLogin ? "✓ Launch at Login" : "Launch at Login") {
                appDelegate.toggleLaunchAtLogin()
            }

            Divider()

            Button("Quit Texmail") {
                NSApplication.shared.terminate(nil)
            }
            .keyboardShortcut("q")
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    let hotkeyManager = HotkeyManager()
    let conversionService = ConversionService()
    var launchAtLogin = false

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Prompt accessibility
        let opts = [kAXTrustedCheckOptionPrompt.takeUnretainedValue(): true] as CFDictionary
        _ = AXIsProcessTrustedWithOptions(opts)

        // Register hotkey
        let cfg = loadConfig()
        hotkeyManager.register(key: cfg.hotkeyKey, modifiers: cfg.hotkeyModifiers) { [weak self] in
            self?.onHotkeyFired()
        }

        // Listen for shortcut changes from UI
        NotificationCenter.default.addObserver(
            self, selector: #selector(hotkeyDidChange(_:)),
            name: .hotkeyChanged, object: nil
        )

        // Check launch at login status
        if #available(macOS 13.0, *) {
            launchAtLogin = SMAppService.mainApp.status == .enabled
        }
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        false
    }

    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        if !flag {
            NSApp.activate(ignoringOtherApps: true)
        }
        return true
    }

    func toggleLaunchAtLogin() {
        if #available(macOS 13.0, *) {
            do {
                if launchAtLogin {
                    try SMAppService.mainApp.unregister()
                } else {
                    try SMAppService.mainApp.register()
                }
                launchAtLogin.toggle()
            } catch {
                print("[Texmail] Launch at login error: \(error)")
            }
        }
    }

    private func onHotkeyFired() {
        let cfg = loadConfig()
        conversionService.performFullConversion(fontSize: cfg.fontSizePt) { _ in }
    }

    @objc private func hotkeyDidChange(_ notification: Notification) {
        guard let key = notification.userInfo?["key"] as? String,
              let mods = notification.userInfo?["mods"] as? [String] else { return }
        hotkeyManager.registerKey(key: key, modifiers: mods)
    }
}
