# -*- coding: utf-8 -*-
"""
数字转换器 - 将带单位的数字（K/M/B/T）转换为中文大写
Windows 原生 UI，低占用，可调大小
"""

import tkinter as tk
from tkinter import ttk
import re

# ── 中文数字转换 ────────────────────────────────────────────

DIGITS = "零一二三四五六七八九"
UNITS_SMALL = ["", "十", "百", "千"]
UNITS_BIG = ["", "万", "亿", "兆"]


def _convert_4digits(n: int) -> str:
    """转换最多四位数字为中文（保留一十）"""
    if n == 0:
        return "零"

    parts = []
    for i in range(4):
        digit = n % 10
        n //= 10
        if digit != 0:
            parts.append(DIGITS[digit] + UNITS_SMALL[i])
        else:
            if parts and parts[-1] != "零":
                parts.append("零")

    while parts and parts[-1] == "零":
        parts.pop()

    return "".join(reversed(parts))


def _convert_group(n: int, *, is_most_significant: bool = False) -> str:
    """转换四位数字为一组。

    is_most_significant=True 时 "一十" 简化为 "十"（如 十万、十亿）；
    内部组保留 "一十"（如 十万零一十、一亿零一十万）。
    """
    s = _convert_4digits(n)
    if is_most_significant and s.startswith("一十"):
        s = s[1:]
    return s


def to_chinese_upper(num: int) -> str:
    """将整数转为中文大写"""
    if num == 0:
        return "零"

    if num < 0:
        return "负" + to_chinese_upper(-num)

    groups = []
    n = num
    while n > 0:
        groups.append(n % 10000)
        n //= 10000

    result_parts = []
    for i in range(len(groups) - 1, -1, -1):
        g = groups[i]
        if g == 0:
            if result_parts and result_parts[-1] != "零":
                result_parts.append("零")
        else:
            is_ms = (i == len(groups) - 1)
            text = _convert_group(g, is_most_significant=is_ms)

            if result_parts and g < 1000:
                result_parts.append("零")

            result_parts.append(text)

        if g != 0 and i > 0:
            result_parts.append(UNITS_BIG[i])

    result = "".join(result_parts)
    result = re.sub(r"零+", "零", result)
    result = result.rstrip("零")

    if not result:
        result = "零"

    return result


def format_number(num: int) -> str:
    """给整数加千分位逗号"""
    return f"{num:,}"


def simplify_number(n: int) -> int:
    """去掉零散尾数，保留 3 位有效数字。

    >>> simplify_number(1534000)
    1530000
    >>> simplify_number(15340)
    15300
    """
    if n == 0:
        return 0
    s = str(n)
    if len(s) <= 3:
        return n
    keep = s[:3]
    zeros = "0" * (len(s) - 3)
    return int(keep + zeros)


# ── 主窗口 ──────────────────────────────────────────────────

UNITS = [
    ("K", "千",      1_000),
    ("M", "百万",    1_000_000),
    ("B", "十亿",    1_000_000_000),
    ("T", "兆",      1_000_000_000_000),
]


class NumberConverter:
    """数字转换器主窗口"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("数字转换器")
        self.root.geometry("380x210")
        self.root.minsize(280, 180)
        self.root.resizable(True, True)

        # 居中显示
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"+{x}+{y}")

        self._unit_buttons: list[ttk.Button] = []
        self._unit_multipliers: dict[str, int] = {}
        self._build_ui()

    def _build_ui(self):
        font_label  = ("Microsoft YaHei UI", 10)
        font_result = ("Microsoft YaHei UI", 11, "bold")
        font_big    = ("Microsoft YaHei UI", 14, "bold")

        main = ttk.Frame(self.root, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        # ── 顶栏：精简开关（替代标题，节省空间）──
        top = ttk.Frame(main)
        top.pack(fill=tk.X, pady=(0, 8))

        self.simplify_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            top,
            text="精简（去掉零散尾数）",
            variable=self.simplify_var,
            command=self._convert,
        ).pack(side=tk.LEFT)

        # ── 输入区 ──
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(
            main,
            textvariable=self.entry_var,
            font=font_label,
            justify="center",
        )
        self.entry.pack(fill=tk.X)

        # ── 单位按钮组 ──
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(8, 6))

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        btn_frame.columnconfigure(3, weight=1)

        self.unit_var = tk.StringVar(value="M")

        for idx, (sym, label, mult) in enumerate(UNITS):
            self._unit_multipliers[sym] = mult
            btn = ttk.Button(
                btn_frame,
                text=f"{sym}\n{label}",
                command=lambda s=sym: self._select_unit(s),
            )
            btn.grid(row=0, column=idx, sticky="ew", padx=1)
            self._unit_buttons.append(btn)

        # ── 结果区（大写在上，数字在下）──
        result_frame = ttk.Frame(main)
        result_frame.pack(fill=tk.BOTH, expand=True)

        # 中文大写（字号更大，放上面避免缩小时被裁切）
        row_cap = ttk.Frame(result_frame)
        row_cap.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(row_cap, text="大写：", font=font_label, width=5).pack(side=tk.LEFT)
        self.cap_label = ttk.Label(
            row_cap, text="—", font=font_big, foreground="#C43E1C",
        )
        self.cap_label.pack(side=tk.LEFT)

        # 数字形式
        row_num = ttk.Frame(result_frame)
        row_num.pack(fill=tk.X)
        ttk.Label(row_num, text="数字：", font=font_label, width=5).pack(side=tk.LEFT)
        self.num_label = ttk.Label(
            row_num, text="—", font=font_result, foreground="#0078D4",
        )
        self.num_label.pack(side=tk.LEFT)

        # ── 初始选中样式 ──
        self._update_button_style("M")

        # ── 自动转换 ──
        self.entry_var.trace_add("write", lambda *_: self._convert())
        self.unit_var.trace_add("write", lambda *_: self._convert())

        self.entry.focus_set()

    def _select_unit(self, sym: str):
        self.unit_var.set(sym)
        self._update_button_style(sym)

    def _update_button_style(self, active: str):
        for btn in self._unit_buttons:
            btn_sym = btn.cget("text").split("\n")[0]
            if btn_sym == active:
                btn.state(["pressed"])
            else:
                btn.state(["!pressed"])

    def _convert(self):
        raw = self.entry_var.get().strip()
        unit = self.unit_var.get()

        if not raw:
            self.num_label.config(text="—", foreground="#0078D4")
            self.cap_label.config(text="—", foreground="#C43E1C")
            return

        try:
            value = float(raw)
        except ValueError:
            self.num_label.config(text="无效数字", foreground="red")
            self.cap_label.config(text="—", foreground="#C43E1C")
            return

        if value < 0:
            self.num_label.config(text="请输入正数", foreground="red")
            self.cap_label.config(text="—", foreground="#C43E1C")
            return

        multiplier = self._unit_multipliers[unit]
        result = value * multiplier

        if result == int(result):
            int_result = int(result)
        else:
            int_result = int(round(result))
            if abs(int_result - result) > 0.001:
                self.num_label.config(
                    text=f"{result:,.6f}".rstrip("0").rstrip("."),
                    foreground="#0078D4",
                )
                self.cap_label.config(text="（仅支持整数大写）", foreground="gray")
                return

        # 精简模式：去掉零散尾数
        if self.simplify_var.get():
            int_result = simplify_number(int_result)

        self.num_label.config(text=format_number(int_result), foreground="#0078D4")
        chinese = to_chinese_upper(int_result)
        self.cap_label.config(text=chinese, foreground="#C43E1C")

    def run(self):
        self.root.mainloop()


# ── 入口 ────────────────────────────────────────────────────

if __name__ == "__main__":
    app = NumberConverter()
    app.run()
