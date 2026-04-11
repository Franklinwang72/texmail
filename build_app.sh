#!/bin/bash
# Build Texmail.app — native Swift macOS app
# Usage: git clone ... && cd latex2clip && ./build_app.sh
set -e
cd "$(dirname "$0")"

PROJECT_DIR="$(pwd)"
VERSION=$(cat VERSION 2>/dev/null || echo "0.1.0")
APP="dist/Texmail.app"
CONTENTS="$APP/Contents"
MACOS="$CONTENTS/MacOS"
RESOURCES="$CONTENTS/Resources"

echo "╔══════════════════════════════════════╗"
echo "║     Building Texmail.app v$VERSION   ║"
echo "╚══════════════════════════════════════╝"

# ── 1. Check Swift compiler + SDK ──
if ! command -v swiftc &>/dev/null; then
    echo "❌ Swift compiler not found. Install Xcode Command Line Tools:"
    echo "   xcode-select --install"
    exit 1
fi
if ! xcrun --show-sdk-path &>/dev/null; then
    echo "❌ macOS SDK not found. Install Xcode Command Line Tools:"
    echo "   xcode-select --install"
    exit 1
fi
SWIFT_VER=$(swiftc --version 2>&1 | grep -oE 'Swift version [0-9]+\.[0-9]+' | head -1)
echo "✓ $SWIFT_VER"

# ── 2. Check/create Python venv ──
PYTHON=""
for p in python3.12 python3.13 python3.14 python3.11 python3.10 python3; do
    if command -v "$p" &>/dev/null; then
        ver=$("$p" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null)
        if [ "$ver" = "True" ]; then
            PYTHON="$(command -v "$p")"
            break
        fi
    fi
done
if [ -z "$PYTHON" ]; then
    echo "❌ Python >= 3.10 not found. Install: brew install python"
    exit 1
fi
echo "✓ $($PYTHON --version)"

if [ ! -f .venv/bin/python ]; then
    echo "  Creating virtual environment..."
    "$PYTHON" -m venv .venv
fi
echo "  Installing Python dependencies..."
.venv/bin/pip install -q -e . 2>&1 | tail -1

# ── 3. Generate icon if needed ──
if [ ! -f resources/latex2clip.icns ]; then
    echo "  Generating icon..."
    .venv/bin/python resources/make_icon.py
fi

# ── 4. Compile Swift ──
echo "  Compiling Swift..."
rm -rf "$APP"
mkdir -p "$MACOS" "$RESOURCES"

SDK_PATH=$(xcrun --show-sdk-path)

swiftc -O -parse-as-library \
    -sdk "$SDK_PATH" \
    -target arm64-apple-macosx13.0 \
    -framework SwiftUI \
    -framework AppKit \
    -framework Carbon \
    -framework ApplicationServices \
    -o "$MACOS/LatexClip" \
    LatexClipApp/*.swift 2>&1

echo "✓ Compiled"

# ── 5. Assemble .app bundle ──
echo -n "$PROJECT_DIR" > "$RESOURCES/project_dir"
cp resources/latex2clip.icns "$RESOURCES/latex2clip.icns"

cat > "$CONTENTS/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Texmail</string>
    <key>CFBundleDisplayName</key>
    <string>Texmail</string>
    <key>CFBundleIdentifier</key>
    <string>com.texmail.app</string>
    <key>CFBundleVersion</key>
    <string>$VERSION</string>
    <key>CFBundleShortVersionString</key>
    <string>$VERSION</string>
    <key>CFBundleExecutable</key>
    <string>LatexClip</string>
    <key>CFBundleIconFile</key>
    <string>latex2clip</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
    <key>LSMinimumSystemVersion</key>
    <string>13.0</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>NSHumanReadableCopyright</key>
    <string>MIT License</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

# ── 6. Deploy ──
rm -rf ~/Desktop/Texmail.app
cp -R "$APP" ~/Desktop/Texmail.app
xattr -cr ~/Desktop/Texmail.app 2>/dev/null || true

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   ✅ Texmail.app on your Desktop     ║"
echo "║   Double-click to launch!            ║"
echo "╚══════════════════════════════════════╝"
