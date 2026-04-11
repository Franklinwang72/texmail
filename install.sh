#!/bin/bash
# Taxmail — one-line installer
# Usage: curl -fsSL https://raw.githubusercontent.com/Franklinwang72/taxmail/main/install.sh | bash
set -e

echo "╔══════════════════════════════════════╗"
echo "║        Installing Taxmail            ║"
echo "╚══════════════════════════════════════╝"

# Where to install
INSTALL_DIR="$HOME/.taxmail"

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

# Check Swift
if ! command -v swiftc &>/dev/null; then
    echo "❌ Swift not found."
    echo "   Install: xcode-select --install"
    exit 1
fi
echo "✓ Swift available"

# Clone or update
if [ -d "$INSTALL_DIR" ]; then
    echo "  Updating..."
    cd "$INSTALL_DIR" && git pull --quiet
else
    echo "  Downloading..."
    git clone --quiet https://github.com/Franklinwang72/taxmail.git "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Build
./build_app.sh

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✅ Taxmail installed!                           ║"
echo "║                                                  ║"
echo "║  App is on your Desktop — double-click to run.   ║"
echo "║                                                  ║"
echo "║  To update later:                                ║"
echo "║    cd ~/.taxmail && git pull && ./build_app.sh   ║"
echo "╚══════════════════════════════════════════════════╝"
