#!/bin/bash
# Texmail — one-line installer
# Usage: curl -fsSL https://raw.githubusercontent.com/Franklinwang72/texmail/main/install.sh | bash
set -e

echo "╔══════════════════════════════════════╗"
echo "║        Installing Texmail            ║"
echo "╚══════════════════════════════════════╝"

INSTALL_DIR="$HOME/.texmail"
VERSION="0.1.0"
RELEASE_URL="https://github.com/Franklinwang72/texmail/releases/download/v${VERSION}/Texmail-v${VERSION}-macos-universal.zip"

# Check Python
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
    echo "❌ Python >= 3.10 not found."
    echo "   Install: brew install python"
    exit 1
fi
echo "✓ $($PYTHON --version)"

# Clone or update repo (for Python engine)
if [ -d "$INSTALL_DIR" ]; then
    echo "  Updating..."
    cd "$INSTALL_DIR" && git pull --quiet
else
    echo "  Downloading..."
    git clone --quiet https://github.com/Franklinwang72/texmail.git "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# Python venv + dependencies
if [ ! -f .venv/bin/python ]; then
    echo "  Creating virtual environment..."
    "$PYTHON" -m venv .venv
fi
echo "  Installing Python dependencies..."
if ! .venv/bin/pip install -e . 2>&1 | grep -v "^\[notice\]"; then
    echo "❌ pip install failed. Check the error above."
    exit 1
fi

# Download pre-built app binary
echo "  Downloading Texmail.app..."
curl -fsSL "$RELEASE_URL" -o /tmp/texmail-release.zip
rm -rf /tmp/texmail-release-extract
mkdir -p /tmp/texmail-release-extract
unzip -q /tmp/texmail-release.zip -d /tmp/texmail-release-extract

# Assemble .app on Desktop
APP=~/Desktop/Texmail.app
rm -rf "$APP"
cp -R /tmp/texmail-release-extract/Texmail.app "$APP"

# Write project dir into app bundle
echo -n "$INSTALL_DIR" > "$APP/Contents/Resources/project_dir"
xattr -cr "$APP" 2>/dev/null || true

# Cleanup
rm -rf /tmp/texmail-release.zip /tmp/texmail-release-extract

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✅ Texmail installed!                           ║"
echo "║                                                  ║"
echo "║  App is on your Desktop — double-click to run.   ║"
echo "║                                                  ║"
echo "║  To update later:                                ║"
echo "║    cd ~/.texmail && git pull && ./build_app.sh   ║"
echo "╚══════════════════════════════════════════════════╝"
