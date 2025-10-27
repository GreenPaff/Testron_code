# core/exporter.py
import os
import json
import csv
from typing import Tuple
from PyQt6.QtWidgets import QApplication
import pandas as pd


def copy_to_clipboard(text: str) -> Tuple[bool, str]:
    """
    将文本复制到系统剪贴板（通过 PyQt 的 clipboard）。
    返回 (success, message)。
    """
    try:
        app = QApplication.instance()
        if app is None:
            return False, "未检测到 Qt 应用实例，无法访问剪贴板。"
        clipboard = app.clipboard()
        clipboard.setText(text)
        return True, "已复制到剪贴板。"
    except Exception as e:
        return False, f"复制失败：{e}"


def export_to_file(generated_data: str, file_path: str) -> Tuple[bool, str]:
    """
    将生成的数据导出到指定文件路径。
    支持格式：.xlsx (Excel), .csv, .json
    返回 (success, message)
    约定：生成文本由若干行组成，空行和以 '#' 开头的注释行会被忽略。
    每个有效行内部以空格分隔单元作为单元格（数组 / 矩阵形式）。
    字符串模式将作为单行写入（不会拆分为多个单元格）。
    """
    if not generated_data or not generated_data.strip():
        return False, "导出失败：生成数据为空。"

    ext = os.path.splitext(file_path)[1].lower()
    # 预处理：拆成有意义的行（去掉注释/空行）
    lines = [ln.rstrip() for ln in generated_data.splitlines()]
    # filter lines that look like data (not comments starting with '#', not separators)
    data_lines = [ln for ln in lines if ln and not ln.strip().startswith("#")]

    try:
        if ext == ".json":
            # 将每行按空格拆分成数组（如果行中没有空格，作为单字符串元素）
            rows = [ln.split() for ln in data_lines]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=2)
            return True, f"已导出 JSON：{file_path}"

        elif ext == ".csv":
            rows = [ln.split() for ln in data_lines]
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            return True, f"已导出 CSV：{file_path}"

        elif ext in (".xls", ".xlsx"):
            # 利用 pandas，将每行拆为列（按空格）
            rows = [ln.split() for ln in data_lines]
            df = pd.DataFrame(rows)
            df.to_excel(file_path, index=False, header=False)
            return True, f"已导出 Excel：{file_path}"

        else:
            return False, f"不支持的导出格式：{ext}（仅支持 .xlsx, .csv, .json）"
    except Exception as e:
        return False, f"导出失败：{e}"

