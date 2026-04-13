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

Write math in plain text with `$...$` or `\[...\]`, select it, and Texmail replaces the formulas with beautifully rendered images. Paste into any email client — Gmail, Apple Mail, Outlook, Thunderbird — and your recipient sees real math, not code.

## How to Use

<p align="center">
  <img width="1000" src="serre.gif" />
</p>

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/Franklinwang72/texmail/main/install.sh | bash
```

Texmail appears on your Desktop. Double-click to launch.

### Requirements

- **macOS 13+** (Ventura or later)
- **Python 3.10+** — `brew install python`
- **Xcode Command Line Tools** — `xcode-select --install`
- **TeX** *(optional, for complex formulas)* — `brew install --cask mactex-no-gui`

## Features

- **Global shortcut** — select text in any app, press ⌘⇧L, formulas are rendered in-place
- **All LaTeX delimiters** — `$...$`, `\(...\)`, `$$...$$`, `\[...\]`
- **Smart rendering** — uses matplotlib for simple math, auto-falls back to xelatex for `amsmath`, `tikz-cd`, matrices, CJK text
- **Customizable** — change shortcut and formula size directly in the app
- **Email-ready** — outputs HTML + RTFD, works with Gmail, Apple Mail, Outlook, Thunderbird
- **Menu bar app** — runs quietly in background, no Dock clutter
- **Computer Modern font** — the classic LaTeX look, just like in academic papers

## Configuration

Settings can be changed in the app window. For advanced options, edit `~/.config/latex2clip/config.toml`.

## Update & Uninstall

```bash
# Update
cd ~/.texmail && git pull && ./build_app.sh

# Uninstall
rm -rf ~/.texmail ~/Desktop/Texmail.app ~/.config/latex2clip
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Contributors

<a href="https://github.com/Franklinwang72">
  <img src="https://github.com/Franklinwang72.png" width="60" height="60" style="border-radius:50%" alt="Franklinwang72" />
</a>
<a href="https://github.com/gengjgg">
  <img src="https://github.com/gengjgg.png" width="60" height="60" style="border-radius:50%" alt="gengjgg" />
</a>
<a href="https://github.com/edoublemanda">
  <img src="https://github.com/edoublemanda.png" width="60" height="60" style="border-radius:50%" alt="edoublemanda" />
</a>
<a href="https://github.com/claude-ai">
  <img src="https://github.com/claude-ai.png" width="60" height="60" style="border-radius:50%" alt="Claude" />
</a>

## License

[MIT](./LICENSE)
