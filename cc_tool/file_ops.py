"""文件操作模块

本模块负责文件复制和模板变量替换。
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple

from .errors import VariableReplaceError
from .models import ProjectContext, CopyResult


def replace_variables_in_file(file_path: Path, context: ProjectContext) -> None:
    """替换文件中的模板变量

    Args:
        file_path: 文件路径
        context: 项目上下文信息

    Raises:
        VariableReplaceError: 变量替换失败
    """
    # 导入变量替换模块中的实现
    from .variables import replace_variables_in_file as replace_vars
    replace_vars(file_path, context)


def copy_template_files(
    template_dir: Path,
    project_dir: Path,
    context: ProjectContext,
    skip_existing: bool = True,
    dry_run: bool = False
) -> CopyResult:
    """复制模板文件到项目目录

    Args:
        template_dir: 模板目录路径
        project_dir: 项目目录路径
        context: 项目上下文信息
        skip_existing: 是否跳过已存在的文件
        dry_run: 预览模式

    Returns:
        CopyResult: 复制结果统计
    """
    copied: List[Path] = []
    skipped: List[Path] = []
    errors: List[Tuple[Path, str]] = []

    # 确保模板目录存在
    if not template_dir.exists():
        errors.append((template_dir, "模板目录不存在"))
        return CopyResult(copied=copied, skipped=skipped, errors=errors)

    # 递归遍历模板目录
    for template_item in template_dir.rglob("*"):
        # 计算相对于模板目录的路径
        try:
            rel_path = template_item.relative_to(template_dir)
        except ValueError:
            # 不应该发生，跳过
            continue

        target_item = project_dir / rel_path

        # 如果是目录，确保目标目录存在（dry-run时不创建）
        if template_item.is_dir():
            if not dry_run:
                target_item.mkdir(parents=True, exist_ok=True)
            continue

        # 至此，template_item是文件
        if target_item.exists():
            if skip_existing:
                # 目标文件已存在，跳过
                skipped.append(target_item)
                continue
            # 如果skip_existing=False，我们将覆盖文件，所以不跳过

        # 准备复制文件
        if not dry_run:
            try:
                # 确保父目录存在
                target_item.parent.mkdir(parents=True, exist_ok=True)
                # 复制文件（跟随符号链接复制内容）
                shutil.copy2(template_item, target_item)
                # 替换文件中的模板变量
                replace_variables_in_file(target_item, context)
                copied.append(target_item)
            except Exception as e:
                errors.append((target_item, f"复制失败: {str(e)}"))
        else:
            # dry-run模式：只记录将要复制的文件
            copied.append(target_item)

    return CopyResult(copied=copied, skipped=skipped, errors=errors)