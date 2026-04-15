#!/bin/bash
# Texmail — one-line installer
# Usage: curl -fsSL https://raw.githubusercontent.com/Franklinwang72/texmail/main/install.sh | bash
set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║        Installing Texmail            ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Checking dependencies..."

INSTALL_DIR="$HOME/.texmail"
VERSION="0.1.0"
RELEASE_URL="https://github.com/Franklinwang72/texmail/releases/download/v${VERSION}/Texmail-v${VERSION}-macos-universal.zip"

# ── 1. git ──
if command -v git &>/dev/null; then
    echo "  ✓ git"
else
    echo "  ✗ git — installing Xcode Command Line Tools..."
    xcode-select --install 2>/dev/null || true
    echo "    Please wait for the install dialog, then re-run this script."
    exit 1
fi

# ── 2. Homebrew ──
if command -v brew &>/dev/null; then
    echo "  ✓ Homebrew"
else
    echo "  ✗ Homebrew — installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add brew to PATH for this session
    if [ -f /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -f /usr/local/bin/brew ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    if command -v brew &>/dev/null; then
        echo "  ✓ Homebrew installed"
    else
        echo "  ❌ Homebrew installation failed. Install manually:"
        echo "     https://brew.sh"
        exit 1
    fi
fi

# ── 3. Python 3.10+ ──
PYTHON=""
for p in python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$p" &>/dev/null; then
        ver=$("$p" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null)
        if [ "$ver" = "True" ]; then
            PYTHON="$(command -v "$p")"
            break
        fi
    fi
done

if [ -n "$PYTHON" ]; then
    echo "  ✓ $($PYTHON --version)"
else
    echo "  ✗ Python 3.10+ — installing via Homebrew..."
    brew install python 2>&1 | tail -3
    # Find the newly installed python
    for p in python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$p" &>/dev/null; then
            ver=$("$p" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null)
            if [ "$ver" = "True" ]; then
                PYTHON="$(command -v "$p")"
                break
            fi
        fi
    done
    if [ -n "$PYTHON" ]; then
        echo "  ✓ $($PYTHON --version)"
    else
        echo "  ❌ Python installation failed. Install manually:"
        echo "     brew install python"
        exit 1
    fi
fi

echo ""
echo "Installing Texmail..."

# ── 4. Clone or update repo ──
if [ -d "$INSTALL_DIR" ]; then
    echo "  Updating source..."
    cd "$INSTALL_DIR" && git pull --quiet
else
    echo "  Downloading source..."
    git clone --quiet https://github.com/Franklinwang72/texmail.git "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# ── 5. Python venv + dependencies ──
if [ ! -f .venv/bin/python ]; then
    echo "  Creating virtual environment..."
    "$PYTHON" -m venv .venv
fi
echo "  Installing Python dependencies..."
if ! .venv/bin/pip install -e . 2>&1 | grep -v "^\[notice\]" | tail -3; then
    echo "  ❌ pip install failed. Check the error above."
    exit 1
fi

# ── 6. Download pre-built app ──
echo "  Downloading Texmail.app..."
curl -fsSL "$RELEASE_URL" -o /tmp/texmail-release.zip
rm -rf /tmp/texmail-release-extract
mkdir -p /tmp/texmail-release-extract
unzip -q /tmp/texmail-release.zip -d /tmp/texmail-release-extract

APP=~/Desktop/Texmail.app
rm -rf "$APP"
cp -R /tmp/texmail-release-extract/Texmail.app "$APP"
echo -n "$INSTALL_DIR" > "$APP/Contents/Resources/project_dir"
xattr -cr "$APP" 2>/dev/null || true
codesign --force --sign - --deep "$APP" 2>/dev/null || true
rm -rf /tmp/texmail-release.zip /tmp/texmail-release-extract

echo "  ✓ Texmail.app on your Desktop"

# ── 7. Check TeX (optional) ──
echo ""
TEX_FOUND=""
for engine in xelatex pdflatex; do
    if command -v "$engine" &>/dev/null; then
        TEX_FOUND="$engine"
        break
    fi
    for d in /Library/TeX/texbin /opt/homebrew/bin /usr/local/bin; do
        if [ -f "$d/$engine" ]; then
            TEX_FOUND="$d/$engine"
            break 2
        fi
    done
done

if [ -n "$TEX_FOUND" ]; then
    echo "  ✓ TeX found ($TEX_FOUND)"
else
    echo "  ⚠ TeX not found."
    echo "    Simple formulas work without TeX."
    echo "    Complex formulas (matrices, tikz-cd, CJK) need TeX."
    echo ""
    read -p "    Install TeX now? (~4GB download) [y/N]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "    Installing MacTeX (this may take a few minutes)..."
        brew install --cask mactex-no-gui 2>&1 | tail -5
        eval "$(/usr/libexec/path_helper)" 2>/dev/null || true
        echo "    ✓ TeX installed"
    else
        echo "    Skipped. You can install later: brew install --cask mactex-no-gui"
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✅ Texmail installed!                           ║"
echo "║                                                  ║"
echo "║  Double-click Texmail.app on your Desktop.       ║"
echo "╚══════════════════════════════════════════════════╝"
