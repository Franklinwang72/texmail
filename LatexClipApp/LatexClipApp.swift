import SwiftUI
import AppKit
import ApplicationServices
// Login Items managed via System Events (works for unsigned apps at any location)

@main
struct TexmailApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        // Menu bar icon
        MenuBarExtra("Texmail", systemImage: "sum") {
            Text("Texmail")
                .font(.headline)

            Divider()

            Button("Convert Clipboard") {
                let cfg = loadConfig()
                appDelegate.conversionService.performFullConversion(fontSize: cfg.fontSizePt) { _ in }
            }

            let cfg = loadConfig()
            Text("Shortcut: \(displayShortcut(key: cfg.hotkeyKey, modifiers: cfg.hotkeyModifiers))")
                .foregroundStyle(.secondary)

            Divider()

            Button("Settings...") {
                appDelegate.showSettings()
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

class AppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate, ObservableObject {
    let hotkeyManager = HotkeyManager()
    let conversionService = ConversionService()
    @Published var launchAtLogin = false

    private var settingsWindow: NSWindow?

    func applicationDidFinishLaunching(_ notification: Notification) {
        let opts = [kAXTrustedCheckOptionPrompt.takeUnretainedValue(): true] as CFDictionary
        _ = AXIsProcessTrustedWithOptions(opts)

        let cfg = loadConfig()
        hotkeyManager.register(key: cfg.hotkeyKey, modifiers: cfg.hotkeyModifiers) { [weak self] in
            self?.onHotkeyFired()
        }

        NotificationCenter.default.addObserver(
            self, selector: #selector(hotkeyDidChange(_:)),
            name: .hotkeyChanged, object: nil
        )

        checkLaunchAtLogin()

        // Hide Dock icon — menu bar only
        NSApp.setActivationPolicy(.accessory)

        // Show settings window on first launch
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.showSettings()
        }
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        false
    }

    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        if !flag { showSettings() }
        return true
    }

    // MARK: - Settings Window

    func showSettings() {
        // Temporarily show in Dock so the window can get focus
        NSApp.setActivationPolicy(.regular)

        if let window = settingsWindow {
            window.makeKeyAndOrderFront(nil)
            NSApp.activate(ignoringOtherApps: true)
            return
        }

        let contentView = NSHostingView(rootView: ContentView())
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 480, height: 400),
            styleMask: [.titled, .closable, .miniaturizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Texmail"
        window.contentView = contentView
        window.center()
        window.isReleasedWhenClosed = false
        window.delegate = self
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        settingsWindow = window
    }

    // MARK: - Launch at Login (via osascript login items — works for any app location)

    func toggleLaunchAtLogin() {
        let appPath = Bundle.main.bundlePath
        if launchAtLogin {
            // Remove login item
            let script = "tell application \"System Events\" to delete login item \"Texmail\""
            Process.launchedProcess(launchPath: "/usr/bin/osascript", arguments: ["-e", script])
            launchAtLogin = false
        } else {
            // Add login item
            let script = "tell application \"System Events\" to make login item at end with properties {path:\"\(appPath)\", hidden:false}"
            Process.launchedProcess(launchPath: "/usr/bin/osascript", arguments: ["-e", script])
            launchAtLogin = true
        }
    }

    private func checkLaunchAtLogin() {
        let script = "tell application \"System Events\" to get the name of every login item"
        let proc = Process()
        proc.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
        proc.arguments = ["-e", script]
        let pipe = Pipe()
        proc.standardOutput = pipe
        try? proc.run()
        proc.waitUntilExit()
        let output = String(data: pipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
        launchAtLogin = output.contains("Texmail")
    }

    // When settings window closes, hide Dock icon again
    func windowWillClose(_ notification: Notification) {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            NSApp.setActivationPolicy(.accessory)
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
