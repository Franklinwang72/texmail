# Contributing to Texmail

Thank you for your interest in contributing! Whether it's a bug report, feature request, typo fix, or a new rendering engine — every contribution is welcome.

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/texmail.git
cd texmail
```

### 2. Set Up Development Environment

```bash
# Python venv + dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Verify
python -m pytest tests/ -v
```

### 3. Build the App

```bash
./build_app.sh
```

This compiles the Swift UI and assembles `Texmail.app` on your Desktop.

## Project Structure

```
texmail/
├── LatexClipApp/          # Swift UI (macOS app shell)
│   ├── LatexClipApp.swift     # App entry, menu bar, lifecycle
│   ├── ContentView.swift      # Settings window UI
│   ├── HotkeyManager.swift    # Carbon global hotkey
│   ├── ConversionService.swift # Calls Python subprocess
│   ├── ShortcutRecorder.swift  # Key combo capture
│   └── Config.swift            # TOML config read/write
├── latex2clip/            # Python engine (the core)
│   ├── parser.py              # LaTeX delimiter detection
│   ├── renderer/              # Formula → PNG rendering
│   │   ├── matplotlib_.py         # Built-in renderer
│   │   └── local_tex.py          # xelatex fallback
│   ├── composer.py            # HTML composition
│   ├── clipboard.py           # macOS clipboard (RTFD + HTML)
│   ├── config.py              # Config management
│   └── cli.py                 # CLI entry point
├── tests/                 # Unit tests
├── build_app.sh           # Build script
└── install.sh             # One-line installer
```

## How to Contribute

### Bug Reports

Open an [issue](https://github.com/Franklinwang72/texmail/issues) with:
- What you did (steps to reproduce)
- What you expected
- What actually happened
- Your macOS version + Python version (`python3 --version`)
- The LaTeX formula that failed (if applicable)

### Feature Requests

Open an issue with the `enhancement` label. Describe the use case, not just the feature.

### Pull Requests

1. Create a branch: `git checkout -b fix/your-fix-name`
2. Make your changes
3. Run tests: `python -m pytest tests/ -v`
4. Build the app: `./build_app.sh`
5. Commit with a clear message: `git commit -m "Fix: description"`
6. Push and open a PR

### What Makes a Good PR

- **One thing per PR** — don't mix a bug fix with a feature
- **Tests included** — if you change `parser.py`, add a test in `test_parser.py`
- **Builds cleanly** — `./build_app.sh` should succeed with no errors

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Docstrings for public functions
- Run `ruff check .` before committing

### Swift

- Standard Swift conventions
- No force unwrapping (`!`) — use `guard let` or `if let`
- Keep functions short and focused

## Running Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v          # All tests
python -m pytest tests/test_parser.py -v  # Parser only
python -m pytest tests/ -k "display"      # Filter by name
```

## Areas Where Help is Wanted

- **Windows / Linux support** — currently macOS only
- **More LaTeX environments** — `\begin{equation}`, `\begin{align}`, etc.
- **Inline preview** — show a preview before replacing
- **Better error messages** — when a formula fails to render
- **Localization** — translate the app UI to more languages
- **Performance** — faster rendering for many formulas

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
