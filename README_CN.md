<p align="center">
    <br> <a href="README.md">English</a> | <b>中文</b>
</p>

<h1 align="center">∑ Texmail</h1>

<p align="center">
    <em>在邮件中发送 LaTeX 公式 —— 选中文字，按快捷键，搞定。</em>
</p>

<p align="center">
  <a href="LICENSE" target="_blank">
    <img alt="MIT License" src="https://img.shields.io/github/license/Franklinwang72/texmail.svg?style=flat-square" />
  </a>
  <a href="https://github.com/Franklinwang72/texmail/stargazers">
    <img alt="Stars" src="https://img.shields.io/github/stars/Franklinwang72/texmail?style=flat-square" />
  </a>
  <a href="https://github.com/Franklinwang72/texmail">
    <img alt="Clones" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FFranklinwang72%2Ftexmail%2Ftraffic%2Fclones.json&query=%24.count&label=clones&style=flat-square&color=blue" />
  </a>
  <img alt="Swift" src="https://img.shields.io/badge/-Swift-F05138?style=flat-square&logo=swift&logoColor=white" />
  <img alt="Python" src="https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img alt="macOS" src="https://img.shields.io/badge/-macOS%2013+-black?style=flat-square&logo=apple&logoColor=white" />
  <img alt="LaTeX" src="https://img.shields.io/badge/-LaTeX-008080?style=flat-square&logo=latex&logoColor=white" />
</p>

用 `$...$` 或 `\[...\]` 写数学公式，选中文字，Texmail 自动把公式渲染成图片。粘贴到 Gmail、Apple Mail、Outlook、Thunderbird —— 收件人看到的就是排版好的数学公式。

## 使用演示

<p align="center">
  <img width="1000" src="serre.gif" />
</p>

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/Franklinwang72/texmail/main/install.sh | bash
```

安装完成后 Texmail.app 出现在桌面，双击打开即可。

### 前提条件

- **macOS 13+**（Ventura 及以上）
- **Python 3.10+** — `brew install python`
- **TeX**（可选，用于复杂公式）— `brew install --cask mactex-no-gui`

## 功能特点

- **全局快捷键** — 在任意应用中选中文字，按 ⌘⇧L，公式原地渲染
- **所有 LaTeX 定界符** — `$...$`、`\(...\)`、`$$...$$`、`\[...\]`
- **智能渲染** — 简单公式用 matplotlib，复杂公式（`amsmath`、`tikz-cd`、矩阵、中文）自动切换 xelatex
- **可自定义** — 在 app 内直接修改快捷键和公式字号
- **邮件兼容** — 输出 HTML + RTFD，支持 Gmail、Apple Mail、Outlook、Thunderbird
- **菜单栏应用** — 后台静默运行，不占 Dock 空间
- **Computer Modern 字体** — 经典 LaTeX 论文字体

## 配置

设置可在 app 窗口中修改。高级选项请编辑 `~/.config/latex2clip/config.toml`。

## 更新与卸载

```bash
# 更新
cd ~/.texmail && git pull && ./build_app.sh

# 卸载
rm -rf ~/.texmail ~/Desktop/Texmail.app ~/.config/latex2clip
```

## 参与贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解规范。

## 贡献者

<a href="https://github.com/Franklinwang72">
  <img src="https://github.com/Franklinwang72.png" width="60" height="60" style="border-radius:50%" alt="Franklinwang72" />
</a>
<a href="https://github.com/gengjgg">
  <img src="https://github.com/gengjgg.png" width="60" height="60" style="border-radius:50%" alt="gengjgg" />
</a>
<a href="https://github.com/edoublemanda">
  <img src="https://github.com/edoublemanda.png" width="60" height="60" style="border-radius:50%" alt="edoublemanda" />
</a>
<a href="https://github.com/anthropics">
  <img src="https://github.com/anthropics.png" width="60" height="60" style="border-radius:50%" alt="Claude (Anthropic)" />
</a>

## 开源协议

[MIT](./LICENSE)
