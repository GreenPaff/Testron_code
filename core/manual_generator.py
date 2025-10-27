# ---------- 将下面的内容保存为 core/manual_generator.py（完整文件） ----------
import random
import string
from typing import Dict


def generate_data(constraints: Dict) -> str:
    data_type = constraints.get("type", "数组")
    n_spec = constraints.get("n", "10")
    m_spec = constraints.get("m", "10")
    groups = int(constraints.get("groups", 1))
    element_type = constraints.get("element_type", "混合")
    custom_chars = constraints.get("custom_chars", "")

    n = _parse_range_to_int(n_spec, default=10)
    m = _parse_range_to_int(m_spec, default=10)

    result_parts = []
    for gi in range(groups):
        header = f"# 组 {gi+1} / 类型: {data_type} / 元素: {element_type} / N={n} M={m}"
        result_parts.append(header)
        if data_type == "数组":
            result_parts.append(_generate_array_str(n, element_type, custom_chars))
        elif data_type == "字符串":
            result_parts.append(_generate_string_str(n, element_type, custom_chars))
        else:
            raise ValueError(f"不支持的数据类型: {data_type}")
        result_parts.append("")  # 空行分隔

    result_parts.append("--- 生成完毕 ---")
    return "\n".join(result_parts)

# ----------------- 辅助函数 -----------------

def _parse_range_to_int(spec: str, default: int = 10) -> int:
    if spec is None:
        return default
    spec = str(spec).strip()
    if not spec:
        return default
    try:
        if "-" in spec:
            a, b = spec.split("-", 1)
            a_i = int(a.strip())
            b_i = int(b.strip())
            if a_i > b_i:
                a_i, b_i = b_i, a_i
            return random.randint(a_i, b_i)
        else:
            return max(1, int(spec))
    except Exception:
        return default


# def _chars_for_element_type(element_type: str) -> str:
#     digits = "123456789"  # per requirement: digits 1-9
#     letters = string.ascii_letters  # a-zA-Z
#     symbols = string.punctuation  # punctuation set
#     typ = (element_type or "").strip()
#     if typ == "数字":
#         return digits
#     elif typ == "字母":
#         return letters
#     elif typ == "符号":
#         return symbols
#     else:
#         # 混合 or unknown
#         return digits + letters + symbols
def _chars_for_element_type(element_type: str, custom_chars: str = "") -> str:
    digits = "123456789"
    letters = string.ascii_letters
    symbols = string.punctuation
    typ = (element_type or "").strip()
    if typ == "数字":
        return digits
    elif typ == "字母":
        return letters
    elif typ == "符号":
        return symbols
    elif typ == "自定义" and custom_chars:
        return custom_chars
    else:
        return digits + letters + symbols


def _generate_array_str(n: int, element_type: str, custom_chars: str = "") -> str:
    pool = _chars_for_element_type(element_type, custom_chars)
    items = [random.choice(pool) for _ in range(n)]
    return " ".join(items)



# def _generate_matrix_str(n: int, m: int, element_type: str) -> str:
#     pool = _chars_for_element_type(element_type)
#     rows = []
#     for _ in range(n):
#         row = " ".join(random.choice(pool) for _ in range(m))
#         rows.append(row)
#     return "\n".join(rows)


def _generate_string_str(n: int, element_type: str, custom_chars: str = "") -> str:
    pool = _chars_for_element_type(element_type, custom_chars)
    return "".join(random.choice(pool) for _ in range(n))


