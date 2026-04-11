import SwiftUI

struct ContentView: View {
    @State private var hotkeyKey: String = "L"
    @State private var hotkeyMods: [String] = ["cmd", "shift"]
    @State private var fontSize: String = "14"
    @State private var statusMessage: String = ""
    @State private var isRecording: Bool = false
    @State private var isConverting: Bool = false

    // Use the shared instance from AppDelegate
    private var service: ConversionService {
        (NSApp.delegate as? AppDelegate)?.conversionService ?? ConversionService()
    }

    var shortcutDisplay: String {
        displayShortcut(key: hotkeyKey, modifiers: hotkeyMods)
    }

    var body: some View {
        VStack(spacing: 0) {

            // ── Header ──
            VStack(spacing: 6) {
                Text("Texmail")
                    .font(.system(size: 28, weight: .bold, design: .rounded))

                Text("LaTeX formulas, ready for email.")
                    .font(.system(size: 13, weight: .regular, design: .default))
                    .foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity)
            .padding(.top, 28)
            .padding(.bottom, 20)

            // ── Settings cards ──
            VStack(spacing: 12) {

                // Shortcut card
                settingsCard {
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Shortcut")
                                .font(.system(size: 13, weight: .semibold))
                            Text("Select text, press shortcut to render")
                                .font(.system(size: 11))
                                .foregroundStyle(.tertiary)
                        }

                        Spacer()

                        Text(isRecording ? "Press keys..." : shortcutDisplay)
                            .font(.system(size: 18, weight: .medium, design: .monospaced))
                            .foregroundStyle(isRecording ? .orange : .primary)
                            .padding(.horizontal, 14)
                            .padding(.vertical, 7)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(isRecording
                                          ? Color.orange.opacity(0.12)
                                          : Color.primary.opacity(0.06))
                            )

                        Button(isRecording ? "Cancel" : "Change") {
                            isRecording.toggle()
                        }
                        .controlSize(.small)
                        .buttonStyle(.bordered)
                    }
                }

                // Font size card
                settingsCard {
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Formula Size")
                                .font(.system(size: 13, weight: .semibold))
                            Text("Match your email font size")
                                .font(.system(size: 11))
                                .foregroundStyle(.tertiary)
                        }

                        Spacer()

                        TextField("14", text: $fontSize)
                            .frame(width: 48)
                            .multilineTextAlignment(.center)
                            .textFieldStyle(.roundedBorder)

                        Text("pt")
                            .font(.system(size: 12))
                            .foregroundStyle(.secondary)

                        Button("Save") {
                            let fs = Double(fontSize) ?? 14.0
                            saveFontSize(fs)
                            statusMessage = "Saved \(Int(fs)) pt"
                        }
                        .controlSize(.small)
                        .buttonStyle(.bordered)
                    }
                }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 20)

            // ── Convert area ──
            VStack(spacing: 10) {
                Button(action: doConvert) {
                    HStack(spacing: 8) {
                        if isConverting {
                            ProgressView()
                                .controlSize(.small)
                        }
                        Image(systemName: isConverting ? "arrow.triangle.2.circlepath" : "wand.and.stars")
                            .font(.system(size: 14))
                        Text(isConverting ? "Converting..." : "Convert Clipboard")
                            .font(.system(size: 14, weight: .medium))
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                }
                .buttonStyle(.borderedProminent)
                .tint(.blue)
                .disabled(isConverting)
                .controlSize(.large)

                if !statusMessage.isEmpty {
                    Text(statusMessage)
                        .font(.system(size: 12))
                        .foregroundStyle(statusMessage.hasPrefix("✅") ? .green :
                                        statusMessage.hasPrefix("❌") ? .red : .secondary)
                        .transition(.opacity)
                }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 20)

            // ── Footer ──
            Text("Copy text with $...$ formulas \u{2192} Convert \u{2192} Paste into email")
                .font(.system(size: 11))
                .foregroundStyle(.quaternary)
                .padding(.bottom, 16)
        }
        .frame(width: 480)
        .background(
            ShortcutRecorderRepresentable(isRecording: $isRecording) { key, mods in
                hotkeyKey = key
                hotkeyMods = mods
                isRecording = false
                saveHotkey(key: key, modifiers: mods)
                NotificationCenter.default.post(name: .hotkeyChanged, object: nil,
                                                userInfo: ["key": key, "mods": mods])
                statusMessage = "Shortcut set to \(displayShortcut(key: key, modifiers: mods))"
            }
            .frame(width: 0, height: 0)
        )
        .onAppear {
            let cfg = loadConfig()
            hotkeyKey = cfg.hotkeyKey
            hotkeyMods = cfg.hotkeyModifiers
            fontSize = cfg.fontSizePt.truncatingRemainder(dividingBy: 1) == 0
                ? "\(Int(cfg.fontSizePt))"
                : String(format: "%.1f", cfg.fontSizePt)
        }
    }

    private func doConvert() {
        isConverting = true
        statusMessage = ""
        let fs = Double(fontSize) ?? 14.0
        saveFontSize(fs)
        DispatchQueue.global(qos: .userInitiated).async {
            let msg = service.convertClipboard(fontSize: fs)
            DispatchQueue.main.async {
                statusMessage = msg
                isConverting = false
            }
        }
    }

    // ── Reusable card container ──
    @ViewBuilder
    private func settingsCard<Content: View>(@ViewBuilder content: () -> Content) -> some View {
        content()
            .padding(.horizontal, 16)
            .padding(.vertical, 14)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.primary.opacity(0.04))
            )
    }
}

extension Notification.Name {
    static let hotkeyChanged = Notification.Name("hotkeyChanged")
}
