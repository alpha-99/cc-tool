"""命令行接口模块

本模块负责解析命令行参数，验证输入，并调用核心业务逻辑。
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from . import constants, logger
from .errors import LanguageNotSupportedError, ProjectDirectoryError


def normalize_language(language: str) -> str:
    """标准化语言名称

    将语言别名转换为标准名称，不区分大小写。

    Args:
        language: 用户输入的语言名称或别名

    Returns:
        标准化的语言名称

    Raises:
        LanguageNotSupportedError: 如果语言不支持
    """
    if not language or not language.strip():
        raise LanguageNotSupportedError(f"语言不能为空")

    lang_lower = language.strip().lower()

    # 查找匹配的标准语言或别名
    for std_lang, aliases in constants.SUPPORTED_LANGUAGES.items():
        if lang_lower == std_lang.lower():
            return std_lang
        if lang_lower in [alias.lower() for alias in aliases]:
            return std_lang

    raise LanguageNotSupportedError(f"不支持的语言: {language}")


def project_dir_type(value: str) -> Path:
    """自定义类型转换函数，用于处理项目目录参数

    Args:
        value: 用户输入的路径字符串

    Returns:
        转换后的Path对象

    Raises:
        argparse.ArgumentTypeError: 如果路径为空字符串
    """
    if value == "":
        # 空字符串会被argparse转换为Path(".")，这不符合预期
        raise argparse.ArgumentTypeError("项目目录路径不能为空")
    # 空白字符（如"   "）将被转换为Path("   ")，后续验证会处理
    return Path(value)


def validate_project_directory(project_dir: Path) -> None:
    """验证项目目录

    Args:
        project_dir: 项目目录路径

    Raises:
        ProjectDirectoryError: 如果目录无效
    """
    # 检查路径是否为空或仅空白字符
    if not project_dir or not str(project_dir).strip():
        raise ProjectDirectoryError("项目目录路径不能为空")

    # 如果项目目录已存在，必须是目录且可写
    if project_dir.exists():
        if not project_dir.is_dir():
            raise ProjectDirectoryError(f"路径已存在但不是目录: {project_dir}")
        # 检查是否可写
        if not os.access(str(project_dir), os.W_OK):
            raise ProjectDirectoryError(f"目录不可写: {project_dir}")
    else:
        # 检查父目录是否存在且可写
        parent = project_dir.parent
        if not parent.exists():
            raise ProjectDirectoryError(f"父目录不存在: {parent}")
        if not os.access(str(parent), os.W_OK):
            raise ProjectDirectoryError(f"父目录不可写: {parent}")


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """解析命令行参数

    Args:
        args: 命令行参数列表，默认为 sys.argv[1:]

    Returns:
        解析后的参数命名空间对象

    Raises:
        LanguageNotSupportedError: 如果语言不支持
        ProjectDirectoryError: 如果项目目录无效
    """
    parser = argparse.ArgumentParser(
        description="初始化 Claude Code 项目配置",
        prog="cc-tool",
    )

    # 位置参数：可选（当使用--list-languages等标志时可省略）
    parser.add_argument(
        "project_dir",
        type=project_dir_type,
        nargs="?",
        help="项目目录路径（使用--list-languages等标志时可省略）"
    )
    parser.add_argument(
        "language",
        type=str,
        nargs="?",
        help="编程语言类型（支持别名）（使用--list-languages等标志时可省略）"
    )

    # 可选参数
    parser.add_argument(
        "--verbose", "-V",
        action="store_true",
        help="详细模式，输出调试信息"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="预览模式，显示将要执行的操作但不实际执行"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式，只输出错误信息"
    )
    parser.add_argument(
        "--list-languages", "-l",
        action="store_true",
        help="列出所有支持的语言类型"
    )
    parser.add_argument(
        "--list-templates", "-t",
        action="store_true",
        help="列出所有可用的模板"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {constants.VERSION}"
    )

    # 解析参数
    parsed_args = parser.parse_args(args)

    # 处理列表标志和版本标志（这些标志优先级最高）
    if parsed_args.list_languages:
        print("支持的语言类型:")
        for lang, aliases in constants.SUPPORTED_LANGUAGES.items():
            alias_str = f" (别名: {', '.join(aliases)})" if aliases else ""
            print(f"  - {lang}{alias_str}")
        sys.exit(0)

    if parsed_args.list_templates:
        print("可用的模板:")
        # TODO: 实现模板列表功能
        print("  功能尚未实现")
        sys.exit(0)

    # 如果到达这里，说明没有使用列表标志，需要验证必需参数
    if parsed_args.project_dir is None:
        parser.error("缺少必需参数：project_dir")
    if parsed_args.language is None:
        parser.error("缺少必需参数：language")

    # 标准化语言名称（可能抛出LanguageNotSupportedError）
    parsed_args.language = normalize_language(parsed_args.language)

    # 验证项目目录（可能抛出ProjectDirectoryError）
    validate_project_directory(parsed_args.project_dir)

    return parsed_args


def main() -> int:
    """命令行主入口点

    Returns:
        退出码（0表示成功，非0表示错误）
    """
    try:
        # 解析命令行参数
        args = parse_args()

        # 配置日志系统
        logger.setup_logger(verbose=args.verbose, quiet=args.quiet)

        # 记录初始化信息
        logger.log_info(f"正在初始化项目: {args.project_dir}")
        logger.log_info(f"使用语言模板: {args.language}")

        # TODO: 调用核心逻辑（待Phase 5实现）
        # from .core import initialize_project
        # result = initialize_project(args.project_dir, args.language,
        #                            verbose=args.verbose, dry_run=args.dry_run)
        # logger.log_info(f"完成！共复制 {result.copied_count} 个文件。")

        logger.log_warning("核心功能尚未实现，此版本仅演示命令行解析")
        return 0

    except (LanguageNotSupportedError, ProjectDirectoryError) as e:
        # 这些异常已经在parse_args中处理，但以防万一
        logger.log_error(str(e))
        return 1
    except Exception as e:
        # 未知异常
        logger.log_error(f"未知错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())