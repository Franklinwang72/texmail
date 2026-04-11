# ∑ Taxmail

[English](README.md) | **中文**

**在邮件中发送 LaTeX 公式 —— 选中文字，按快捷键，搞定。**

用 `$...$` 或 `\[...\]` 写数学公式，选中文字，Taxmail 自动把公式渲染成图片。粘贴到任何邮件客户端 —— Gmail、Apple Mail、Outlook —— 收件人看到的就是排版好的数学公式。

## 使用演示

![使用演示](how_to_use.gif)

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/Franklinwang72/taxmail/main/install.sh | bash
```

安装完成后 Taxmail.app 出现在桌面，双击打开即可。

### 前提条件

- **macOS 13+**（Ventura 及以上）
- **Python 3.10+** — `brew install python@3.12`
- **Xcode 命令行工具** — `xcode-select --install`
- **TeX**（可选，用于复杂公式）— `brew install --cask mactex-no-gui`

## 使用方法

### 方法一：快捷键（推荐）

1. 在任意应用中写含 LaTeX 公式的文字
2. **选中文字**
3. 按 **⌘⇧L**（可在设置中自定义）
4. 公式自动渲染并原地替换

### 方法二：剪贴板

1. **复制** 含公式的文字（⌘C）
2. 在 Taxmail 窗口点 **Convert Clipboard**
3. **粘贴** 到邮件中（⌘V）

### 方法三：右键菜单

1. 选中文字 → **右键** → **服务** → **Taxmail**

## 支持的 LaTeX 语法

| 定界符 | 类型 | 示例 |
|--------|------|------|
| `$...$` | 行内公式 | `$x^2 + y^2 = r^2$` |
| `\(...\)` | 行内公式 | `\(E = mc^2\)` |
| `$$...$$` | 行间公式 | `$$\int_0^\infty e^{-x} dx$$` |
| `\[...\]` | 行间公式 | `\[\sum_{n=1}^{\infty} \frac{1}{n^2}\]` |

### 渲染引擎

- **matplotlib**（内置）— 处理常见数学符号：分式、积分、希腊字母、上下标
- **xelatex**（自动检测）— 完整 LaTeX 支持，包括 `amsmath`、`tikz-cd`、中文 `\text{}`、`\begin{cases}` 等

如果你装了 TeX，Taxmail 会自动在 matplotlib 渲染失败时切换到 xelatex。

## 设置

Taxmail 窗口可以：

- **更改快捷键** — 点 "Change"，按下你想要的组合键
- **设置公式字号** — 匹配邮件字号（如 12pt、14pt、16pt）

设置保存在 `~/.config/latex2clip/config.toml`。

## 邮件客户端兼容性

| 客户端 | 状态 | 说明 |
|--------|------|------|
| Gmail (Chrome) | ✅ | 使用 HTML + base64 图片 |
| Apple Mail | ✅ | 使用 RTFD 内嵌图片 |
| Outlook (网页版) | ✅ | 支持行内图片 |
| Thunderbird | ✅ | 使用 HTML |

## 更新

```bash
cd ~/.taxmail && git pull && ./build_app.sh
```

## 卸载

```bash
rm -rf ~/.taxmail ~/Desktop/Taxmail.app ~/.config/latex2clip
```

## 开源协议

MIT
