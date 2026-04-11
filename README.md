<p align="center">
    <br> <b>English</b> | <a href="README_CN.md">中文</a>
</p>

<h1 align="center">∑ Texmail</h1>

<p align="center">
    <em>Render LaTeX formulas for email — select, press shortcut, done.</em>
</p>

<p align="center">
  <a href="LICENSE" target="_blank">
    <img alt="MIT License" src="https://img.shields.io/github/license/Franklinwang72/texmail.svg?style=flat-square" />
  </a>
  <img alt="Swift" src="https://img.shields.io/badge/-Swift-F05138?style=flat-square&logo=swift&logoColor=white" />
  <img alt="Python" src="https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img alt="macOS" src="https://img.shields.io/badge/-macOS%2013+-black?style=flat-square&logo=apple&logoColor=white" />
  <img alt="LaTeX" src="https://img.shields.io/badge/-LaTeX-008080?style=flat-square&logo=latex&logoColor=white" />
</p>

Write math in plain text with `$...$` or `\[...\]`, select it, and Texmail replaces the formulas with beautifully rendered images. Paste into any email client — Gmail, Apple Mail, Outlook — and your recipient sees real math, not code.

## How to Use

<p align="center">
  <img width="800" src="serre.gif" />
</p>

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/Franklinwang72/texmail/main/install.sh | bash
```

This installs Texmail to your Desktop. Double-click to launch.

### Requirements

- **macOS 13+** (Ventura or later)
- **Python 3.10+** — `brew install python`
- **Xcode Command Line Tools** — `xcode-select --install`
- **TeX** *(optional, for complex formulas)* — `brew install --cask mactex-no-gui`

## Features

1. **Global shortcut** — select text in any app, press ⌘⇧L, formulas are rendered in-place
2. **Multiple LaTeX delimiters** — `$...$`, `\(...\)`, `$$...$$`, `\[...\]`
3. **Auto TeX detection** — automatically uses xelatex when installed for full LaTeX support
4. **Customizable** — change shortcut, formula size, colors in the app
5. **Email-ready** — outputs HTML + RTFD for Gmail, Apple Mail, Outlook, Thunderbird
6. **Menu bar icon** — runs in background, always ready
7. **CJK support** — Chinese, Japanese, Korean text in `\text{}` works out of the box
8. **tikz-cd support** — commutative diagrams render correctly

## Supported LaTeX Syntax

| Delimiter | Type | Example |
|-----------|------|---------|
| `$...$` | Inline | `$x^2 + y^2 = r^2$` |
| `\(...\)` | Inline | `\(E = mc^2\)` |
| `$$...$$` | Display | `$$\int_0^\infty e^{-x} dx$$` |
| `\[...\]` | Display | `\[\sum_{n=1}^{\infty} \frac{1}{n^2}\]` |

### Rendering Engines

- **matplotlib** (built-in) — handles common math: fractions, integrals, Greek letters, subscripts
- **xelatex** (auto-detected) — full LaTeX support including `amsmath`, `tikz-cd`, CJK text, matrices

If TeX is installed, Texmail automatically falls back to it for formulas matplotlib can't handle.

## Configuration

Settings are saved to `~/.config/latex2clip/config.toml`.

```toml
[hotkey]
key = "L"
modifiers = ["cmd", "shift"]

[render]
engine = "auto"        # auto | matplotlib | latex
dpi = 300
font_size_pt = 14.0
fg_color = "#000000"
bg_color = "#FFFFFF"
```

## Architecture

```
┌─────────────────────────────────┐
│  Swift App (UI + global hotkey) │
│  ┌───────────┐  ┌────────────┐  │
│  │ SwiftUI   │  │ Carbon     │  │
│  │ Settings  │  │ Hotkey     │  │
│  └───────────┘  └─────┬──────┘  │
│                       │         │
│            subprocess │         │
│                       ▼         │
│  ┌─────────────────────────┐    │
│  │  Python Engine          │    │
│  │  parser → renderer →    │    │
│  │  composer → clipboard   │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
```

## Email Client Compatibility

| Client | Status | Notes |
|--------|--------|-------|
| Gmail (Chrome) | ✅ | HTML with base64 images |
| Apple Mail | ✅ | RTFD with embedded images |
| Outlook | ✅ | Inline images |
| Thunderbird | ✅ | HTML |

## Update

```bash
cd ~/.texmail && git pull && ./build_app.sh
```

## Uninstall

```bash
rm -rf ~/.texmail ~/Desktop/Texmail.app ~/.config/latex2clip
```

## License

[MIT](./LICENSE)
