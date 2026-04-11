import Foundation

struct AppConfig {
    var hotkeyKey: String = "L"
    var hotkeyModifiers: [String] = ["cmd", "shift"]
    var fontSizePt: Double = 14.0
    var engine: String = "auto"
    var dpi: Int = 300
}

func loadConfig() -> AppConfig {
    var cfg = AppConfig()
    let path = NSHomeDirectory() + "/.config/latex2clip/config.toml"
    guard let content = try? String(contentsOfFile: path, encoding: .utf8) else { return cfg }

    var currentSection = ""
    for line in content.components(separatedBy: "\n") {
        let trimmed = line.trimmingCharacters(in: .whitespaces)
        if trimmed.hasPrefix("[") && trimmed.hasSuffix("]") {
            currentSection = String(trimmed.dropFirst().dropLast())
            continue
        }
        guard let eqIdx = trimmed.firstIndex(of: "=") else { continue }
        let key = trimmed[trimmed.startIndex..<eqIdx].trimmingCharacters(in: .whitespaces)
        let val = trimmed[trimmed.index(after: eqIdx)...].trimmingCharacters(in: .whitespaces)

        func unquote(_ s: String) -> String {
            if s.hasPrefix("\"") && s.hasSuffix("\"") && s.count >= 2 {
                return String(s.dropFirst().dropLast())
            }
            return s
        }

        switch (currentSection, key) {
        case ("hotkey", "key"):
            cfg.hotkeyKey = unquote(val)
        case ("hotkey", "modifiers"):
            // Parse ["cmd", "shift"] format
            let inner = val.replacingOccurrences(of: "[", with: "")
                          .replacingOccurrences(of: "]", with: "")
            cfg.hotkeyModifiers = inner.components(separatedBy: ",")
                .map { $0.trimmingCharacters(in: .whitespaces) }
                .map { unquote($0) }
                .filter { !$0.isEmpty }
        case ("render", "font_size_pt"):
            cfg.fontSizePt = Double(val) ?? 12.0
        case ("render", "engine"):
            cfg.engine = unquote(val)
        case ("render", "dpi"):
            cfg.dpi = Int(val) ?? 300
        default:
            break
        }
    }
    return cfg
}

// Serial queue to prevent concurrent config writes
private let configQueue = DispatchQueue(label: "com.taxmail.config")

private func configPath() -> String {
    let dir = NSHomeDirectory() + "/.config/latex2clip"
    try? FileManager.default.createDirectory(atPath: dir, withIntermediateDirectories: true)
    return dir + "/config.toml"
}

private func readConfig() -> String {
    (try? String(contentsOfFile: configPath(), encoding: .utf8)) ?? ""
}

private func writeConfig(_ content: String) {
    do {
        try content.write(toFile: configPath(), atomically: true, encoding: .utf8)
    } catch {
        print("[Taxmail] Failed to save config: \(error)")
    }
}

func saveHotkey(key: String, modifiers: [String]) {
    configQueue.sync {
        var content = readConfig()

        let safeKey = key.replacingOccurrences(of: "\"", with: "")
        let modsStr = modifiers.map { "\"\($0)\"" }.joined(separator: ", ")

        // Replace only the key= and modifiers= lines, preserving comments
        if content.contains("[hotkey]") {
            if let range = content.range(of: #"key\s*=\s*\"[^\"]*\""#, options: .regularExpression) {
                content.replaceSubrange(range, with: "key = \"\(safeKey)\"")
            }
            if let range = content.range(of: #"modifiers\s*=\s*\[.*?\]"#, options: .regularExpression) {
                content.replaceSubrange(range, with: "modifiers = [\(modsStr)]")
            }
        } else {
            content += "\n[hotkey]\nkey = \"\(safeKey)\"\nmodifiers = [\(modsStr)]\n"
        }

        writeConfig(content)
    }
}

func saveFontSize(_ size: Double) {
    configQueue.sync {
        var content = readConfig()
        if let range = content.range(of: #"font_size_pt\s*=\s*[\d.]+"#, options: .regularExpression) {
            content.replaceSubrange(range, with: "font_size_pt = \(size)")
        }
        writeConfig(content)
    }
}
