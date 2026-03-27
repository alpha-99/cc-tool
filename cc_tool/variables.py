"""变量替换模块

本模块负责处理模板文件中的变量替换逻辑。
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional

from .errors import VariableReplaceError
from .constants import VARIABLE_PATTERN, SUPPORTED_VARIABLES
from .models import ProjectContext


def _is_binary_file(file_path: Path) -> bool:
    """检查文件是否为二进制文件

    Args:
        file_path: 文件路径

    Returns:
        bool: 如果是二进制文件返回True，否则返回False
    """
    # 常见二进制文件扩展名
    binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.exe', '.dll', '.so', '.bin'}
    if file_path.suffix.lower() in binary_extensions:
        return True

    # 尝试检测编码，如果能成功检测到编码，则不是二进制文件
    encoding = _detect_encoding(file_path)
    if encoding is not None:
        return False

    # 无法检测编码，可能是二进制文件
    return True


def _detect_encoding(file_path: Path) -> Optional[str]:
    """检测文件编码

    Args:
        file_path: 文件路径

    Returns:
        str: 检测到的编码，如果无法检测则返回None
    """
    # 读取文件全部字节内容
    content_bytes = file_path.read_bytes()

    # 检查BOM
    if content_bytes.startswith(b'\xef\xbb\xbf'):
        return 'utf-8-sig'
    elif content_bytes.startswith(b'\xff\xfe'):
        return 'utf-16-le'
    elif content_bytes.startswith(b'\xfe\xff'):
        return 'utf-16-be'

    # 尝试常见编码（包括更多编码变体）
    encodings_to_try = ['utf-8', 'utf-8-sig', 'utf-16-le', 'utf-16-be', 'utf-32', 'latin-1', 'ascii', 'gbk', 'gb2312', 'big5']

    # 用于评估解码文本质量的函数
    def text_quality(text: str) -> int:
        """评估文本质量，返回可打印字符的数量"""
        import string
        # 可打印字符包括字母、数字、标点、空格
        printable = set(string.printable)
        # 中文字符范围
        chinese_ranges = [
            (0x4E00, 0x9FFF),  # 常用汉字
            (0x3400, 0x4DBF),  # 扩展A
            (0x20000, 0x2A6DF), # 扩展B (但Python字符串是UTF-16，可能需要代理对)
        ]
        score = 0
        for char in text:
            if char in printable:
                score += 1
            else:
                # 检查是否为中文字符
                code = ord(char)
                for start, end in chinese_ranges:
                    if start <= code <= end:
                        score += 1
                        break
        # 额外加分：如果包含模板变量占位符{{}}
        if '{{' in text and '}}' in text:
            score += 100
        # 额外加分：如果包含中文字符（已计入）
        # 额外加分：如果包含常见标点
        if any(c in text for c in [':', '-', '(', ')', '[', ']', '{', '}']):
            score += 10
        return score

    best_encoding = None
    best_score = -1

    for encoding in encodings_to_try:
        try:
            decoded = content_bytes.decode(encoding)
            score = text_quality(decoded)
            # 如果得分比当前最佳高，更新
            if score > best_score:
                best_score = score
                best_encoding = encoding
        except UnicodeDecodeError:
            continue

    return best_encoding


def _replace_variables_in_text(content: str, context: ProjectContext) -> str:
    """替换文本内容中的变量

    Args:
        content: 文本内容
        context: 项目上下文信息

    Returns:
        str: 替换变量后的文本内容
    """
    # 构建变量映射
    variable_map: Dict[str, str] = {
        "PROJECT_NAME": context.project_name,
        "PROJECT_DIR": str(context.project_dir),
        "LANGUAGE": context.language,
    }

    def replace_match(match: re.Match) -> str:
        """替换单个匹配的变量"""
        variable_name = match.group(1)
        if variable_name in SUPPORTED_VARIABLES:
            return variable_map.get(variable_name, match.group(0))
        # 不支持的变量名，保留原样
        return match.group(0)

    # 使用正则表达式替换所有支持的变量
    return re.sub(VARIABLE_PATTERN, replace_match, content)


def replace_variables_in_file(file_path: Path, context: ProjectContext) -> None:
    """替换文件中的模板变量

    Args:
        file_path: 文件路径
        context: 项目上下文信息

    Raises:
        VariableReplaceError: 变量替换失败
    """
    # 检查文件是否存在
    if not file_path.exists():
        raise VariableReplaceError(f"文件不存在: {file_path}")

    # 检查是否为文件
    if not file_path.is_file():
        raise VariableReplaceError(f"路径不是文件: {file_path}")

    # 检查是否为二进制文件
    if _is_binary_file(file_path):
        return

    # 检测文件编码
    encoding = _detect_encoding(file_path)

    # 如果无法检测编码，视为二进制文件，不进行替换
    if encoding is None:
        return

    try:
        # 读取文件内容（使用检测到的编码）
        content = file_path.read_text(encoding=encoding)

        # 替换变量
        new_content = _replace_variables_in_text(content, context)

        # 如果内容有变化，写回文件（使用相同编码）
        if new_content != content:
            file_path.write_text(new_content, encoding=encoding)

    except (UnicodeDecodeError, UnicodeEncodeError):
        # 编码检测失败或编码不支持文件内容
        # 在这种情况下，我们选择不进行变量替换
        # 测试中会跳过不支持的编码
        return
    except (IOError, OSError) as e:
        raise VariableReplaceError(f"文件操作失败: {e}")