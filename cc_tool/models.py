"""核心数据结构定义

本模块定义了cc-tool项目中使用的核心数据结构。
所有数据结构都使用dataclass，便于类型注解和序列化。
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path


@dataclass
class TemplateConfig:
    """模板配置信息

    用于描述一个语言模板的配置信息。

    Attributes:
        language: 语言类型（如 'python'）
        alias: 语言别名列表（如 ['py', 'python3']）
        template_dir: 模板目录路径
        required_files: 必须包含的文件列表
    """

    language: str
    alias: List[str]
    template_dir: Path
    required_files: List[str]


@dataclass
class ProjectContext:
    """项目上下文信息

    包含初始化项目所需的所有上下文信息。

    Attributes:
        project_dir: 项目目录路径
        project_name: 项目名称（从目录名提取）
        language: 编程语言类型
        verbose: 详细模式标志
        dry_run: 预览模式标志
        quiet: 静默模式标志
    """

    project_dir: Path
    project_name: str
    language: str
    verbose: bool
    dry_run: bool
    quiet: bool


@dataclass
class CopyResult:
    """文件复制结果

    记录文件复制操作的结果统计。

    Attributes:
        copied: 成功复制的文件路径列表
        skipped: 跳过的文件路径列表（已存在）
        errors: 错误列表，每个元素为（文件路径，错误信息）元组
    """

    copied: List[Path]
    skipped: List[Path]
    errors: List[Tuple[Path, str]]


@dataclass
class GitignoreRule:
    """Gitignore规则定义

    用于组织.gitignore规则，按类别分组。

    Attributes:
        category: 规则类别（如 'Claude Code', 'IDE', 'OS'）
        rules: 规则内容列表
    """

    category: str
    rules: List[str]