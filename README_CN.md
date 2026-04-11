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
  <img alt="Swift" src="https://img.shields.io/badge/-Swift-F05138?style=flat-square&logo=swift&logoColor=white" />
  <img alt="Python" src="https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img alt="macOS" src="https://img.shields.io/badge/-macOS%2013+-black?style=flat-square&logo=apple&logoColor=white" />
  <img alt="LaTeX" src="https://img.shields.io/badge/-LaTeX-008080?style=flat-square&logo=latex&logoColor=white" />
</p>

用 `$...$` 或 `\[...\]` 写数学公式，选中文字，Texmail 自动把公式渲染成图片。粘贴到任何邮件客户端 —— Gmail、Apple Mail、Outlook —— 收件人看到的就是排版好的数学公式。

## 使用演示

<p align="center">
  <img width="800" src="serre.gif" />
</p>

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/Franklinwang72/texmail/main/install.sh | bash
```

安装完成后 Texmail.app 出现在桌面，双击打开即可。

### 前提条件

- **macOS 13+**（Ventura 及以上）
- **Python 3.10+** — `brew install python`
- **Xcode 命令行工具** — `xcode-select --install`
- **TeX**（可选，用于复杂公式）— `brew install --cask mactex-no-gui`

## 功能特点

1. **全局快捷键** — 在任意应用中选中文字，按 ⌘⇧L，公式原地渲染
2. **多种 LaTeX 定界符** — `$...$`、`\(...\)`、`$$...$$`、`\[...\]`
3. **自动检测 TeX** — 安装了 xelatex 时自动使用，支持完整 LaTeX 语法
4. **可自定义** — 在 app 内修改快捷键、公式字号
5. **邮件兼容** — 输出 HTML + RTFD，兼容 Gmail、Apple Mail、Outlook、Thunderbird
6. **菜单栏图标** — 后台运行，随时待命
7. **中日韩支持** — `\text{}` 中的中文可正常渲染
8. **tikz-cd 支持** — 交换图可正常渲染

## 支持的 LaTeX 语法

| 定界符 | 类型 | 示例 |
|--------|------|------|
| `$...$` | 行内公式 | `$x^2 + y^2 = r^2$` |
| `\(...\)` | 行内公式 | `\(E = mc^2\)` |
| `$$...$$` | 行间公式 | `$$\int_0^\infty e^{-x} dx$$` |
| `\[...\]` | 行间公式 | `\[\sum_{n=1}^{\infty} \frac{1}{n^2}\]` |

### 渲染引擎

- **matplotlib**（内置）— 处理常见数学符号：分式、积分、希腊字母、上下标
- **xelatex**（自动检测）— 完整 LaTeX 支持，包括 `amsmath`、`tikz-cd`、中文 `\text{}`、矩阵

如果你装了 TeX，Texmail 会自动在 matplotlib 渲染失败时切换到 xelatex。

## 配置

设置保存在 `~/.config/latex2clip/config.toml`。

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

## 邮件客户端兼容性

| 客户端 | 状态 | 说明 |
|--------|------|------|
| Gmail (Chrome) | ✅ | HTML + base64 图片 |
| Apple Mail | ✅ | RTFD 内嵌图片 |
| Outlook | ✅ | 行内图片 |
| Thunderbird | ✅ | HTML |

## 更新

```bash
cd ~/.texmail && git pull && ./build_app.sh
```

## 卸载

```bash
rm -rf ~/.texmail ~/Desktop/Texmail.app ~/.config/latex2clip
```

## 开源协议

[MIT](./LICENSE)
