# kmbt-to-chinese

> ⚠️ 此项目代码由 DeepSeek 生成，人工仅做审核与微调。

把英文数字单位缩写（K / M / B / T）一键转为**中文大写**和**阿拉伯数字**的小工具。

纯 Windows 原生窗口，体积极小，输入即出结果。

## 界面

```text
 ☑ 精简（去掉零散尾数）
 ┌──────────────────────┐
 │        1.534         │
 └──────────────────────┘
  [ K ]  [ M ]  [ B ]  [ T ]
    千     百万   十亿    兆
 ──────────────────────────
 大写：一百五十三万
 数字：1,530,000
```

## 功能

- **即时转换** — 键入即出结果，无需点击按钮
- **四种单位** — K（千）、M（百万）、B（十亿）、T（兆）
- **平铺切换** — 单位按钮一字排开，所见即所得
- **精简模式** — 自动去掉零散尾数，保留 3 位有效数字，一眼看懂
- **窗口可调** — 随意拉伸，最小 280×180
- **零依赖** — 仅用 Python 标准库 tkinter，无需安装任何第三方包

## 下载

> [GitHub Releases](https://github.com/jiahuli/kmbt-to-chinese/releases) 下载 `kmbt-to-chinese.exe`，双击即用，无控制台弹窗。

## 从源码运行

```bash
# 控制台版本（有黑框）
python kmbt-to-chinese.py

# 无控制台版本（推荐日常使用）
pythonw kmbt-to-chinese.pyw
```

要求 Python 3.8+（Windows 自带 tkinter 即可，无需额外安装）。

## 打包为 exe

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "kmbt-to-chinese" kmbt-to-chinese.py
# 输出在 dist/kmbt-to-chinese.exe
```

## 许可

MIT License
