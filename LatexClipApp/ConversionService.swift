import AppKit
import Foundation

class ConversionService {
    let projectDir: String

    init() {
        // Read project dir from app bundle Resources
        if let path = Bundle.main.path(forResource: "project_dir", ofType: nil),
           let dir = try? String(contentsOfFile: path, encoding: .utf8) {
            projectDir = dir.trimmingCharacters(in: .whitespacesAndNewlines)
        } else {
            // Fallback: assume .app is inside project/dist/
            let appPath = Bundle.main.bundlePath
            projectDir = (appPath as NSString)
                .deletingLastPathComponent  // dist/
                .appending("/..")           // project/
        }
    }

    private var pythonPath: String {
        projectDir + "/.venv/bin/python"
    }

    private var cliPath: String {
        projectDir + "/.venv/bin/latex2clip"
    }

    // MARK: - Full pipeline: copy → convert → paste

    func performFullConversion(fontSize: Double, completion: @escaping (String) -> Void) {
        // 1. Copy selection (must be on main thread for CGEvent)
        simulateKey(code: 0x08, flags: .maskCommand) // Cmd+C

        // 2. Wait for clipboard, then convert on background thread
        DispatchQueue.global(qos: .userInitiated).asyncAfter(deadline: .now() + 0.35) { [self] in
            let result = runConvert(fontSize: fontSize)

            // 3. Paste back on main thread
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
                if result.success {
                    self.simulateKey(code: 0x09, flags: .maskCommand) // Cmd+V
                }
                self.showNotification(result.message)
                completion(result.message)
            }
        }
    }

    // MARK: - Clipboard-only convert (manual button)

    func convertClipboard(fontSize: Double) -> String {
        let result = runConvert(fontSize: fontSize)
        return result.message
    }

    // MARK: - Python subprocess

    private func runConvert(fontSize: Double) -> (success: Bool, message: String) {
        guard FileManager.default.isExecutableFile(atPath: cliPath) else {
            return (false, "❌ latex2clip not found at \(cliPath)")
        }

        saveFontSize(fontSize)

        let process = Process()
        process.executableURL = URL(fileURLWithPath: cliPath)
        process.arguments = ["convert"]
        process.currentDirectoryURL = URL(fileURLWithPath: projectDir)

        var env = ProcessInfo.processInfo.environment
        // Prepend common TeX paths to existing PATH (preserves user's shell PATH)
        let texPaths = "/Library/TeX/texbin:/opt/homebrew/bin:/usr/local/bin"
        let existingPath = env["PATH"] ?? "/usr/bin:/bin"
        env["PATH"] = texPaths + ":" + existingPath
        env["HOME"] = NSHomeDirectory()
        process.environment = env

        let outPipe = Pipe()
        let errPipe = Pipe()
        process.standardOutput = outPipe
        process.standardError = errPipe

        // Collect output asynchronously to avoid pipe deadlock
        var outData = Data()
        var errData = Data()
        outPipe.fileHandleForReading.readabilityHandler = { h in outData.append(h.availableData) }
        errPipe.fileHandleForReading.readabilityHandler = { h in errData.append(h.availableData) }

        do {
            try process.run()
        } catch {
            return (false, "❌ \(error.localizedDescription)")
        }

        // Wait with timeout (120 seconds — complex formulas with xelatex can be slow)
        let deadline = Date().addingTimeInterval(120)
        while process.isRunning && Date() < deadline {
            Thread.sleep(forTimeInterval: 0.1)
        }
        if process.isRunning {
            process.terminate()
            return (false, "❌ 转换超时")
        }

        outPipe.fileHandleForReading.readabilityHandler = nil
        errPipe.fileHandleForReading.readabilityHandler = nil

        let stdout = String(data: outData, encoding: .utf8) ?? ""
        let stderr = String(data: errData, encoding: .utf8) ?? ""

        if process.terminationStatus == 0 {
            let msg = stdout.trimmingCharacters(in: .whitespacesAndNewlines)
            if msg.contains("Converted") {
                let n = msg.components(separatedBy: " ").compactMap { Int($0) }.first ?? 0
                return (true, "✅ 已转换 \(n) 个公式")
            }
            return (true, "✅ 转换完成")
        } else {
            let errMsg = (stderr + stdout).trimmingCharacters(in: .whitespacesAndNewlines)
            if errMsg.contains("No LaTeX") || errMsg.contains("not found") {
                return (false, "❌ 未检测到公式")
            }
            if errMsg.contains("empty") || errMsg.contains("为空") {
                return (false, "❌ 剪贴板为空")
            }
            return (false, "❌ \(String(errMsg.prefix(100)))")
        }
    }

    // MARK: - CGEvent key simulation

    private func simulateKey(code: CGKeyCode, flags: CGEventFlags) {
        let source = CGEventSource(stateID: .hidSystemState)
        guard let down = CGEvent(keyboardEventSource: source, virtualKey: code, keyDown: true),
              let up = CGEvent(keyboardEventSource: source, virtualKey: code, keyDown: false) else { return }
        down.flags = flags
        up.flags = flags
        down.post(tap: .cghidEventTap)
        up.post(tap: .cghidEventTap)
    }

    // MARK: - Notification

    private func showNotification(_ message: String) {
        // Escape quotes and backslashes to prevent osascript injection
        let safe = message
            .replacingOccurrences(of: "\\", with: "\\\\")
            .replacingOccurrences(of: "\"", with: "\\\"")
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
        process.arguments = ["-e", "display notification \"\(safe)\" with title \"Taxmail\""]
        try? process.run()
    }
}
