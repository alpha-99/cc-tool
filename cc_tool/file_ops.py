"""文件操作模块

本模块负责文件复制和模板变量替换。
"""

from pathlib import Path

from .errors import VariableReplaceError
from .models import ProjectContext


def replace_variables_in_file(file_path: Path, context: ProjectContext) -> None:
    """替换文件中的模板变量

    Args:
        file_path: 文件路径
        context: 项目上下文信息

    Raises:
        VariableReplaceError: 变量替换失败
    """
    raise NotImplementedError("replace_variables_in_file not implemented yet")