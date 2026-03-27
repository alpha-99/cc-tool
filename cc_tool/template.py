"""模板管理模块

本模块负责查找和验证语言模板。
"""

from pathlib import Path
from typing import Optional

from .errors import LanguageNotSupportedError, TemplateNotFoundError
from .models import TemplateConfig


def find_template(language: str) -> TemplateConfig:
    """查找指定语言的模板

    Args:
        language: 编程语言类型

    Returns:
        TemplateConfig: 模板配置信息

    Raises:
        LanguageNotSupportedError: 语言不支持
        TemplateNotFoundError: 模板不存在
    """
    # 导入常量
    from .constants import SUPPORTED_LANGUAGES, REQUIRED_TEMPLATE_FILES

    # 清理输入：去除空白字符，转为小写
    if not language or not isinstance(language, str):
        raise LanguageNotSupportedError(f"Language must be a non-empty string")

    language_clean = language.strip().lower()
    if not language_clean:
        raise LanguageNotSupportedError(f"Language cannot be empty or whitespace only")

    # 查找标准语言名称
    standard_language = None
    alias_list = []

    for std_lang, aliases in SUPPORTED_LANGUAGES.items():
        # 检查是否匹配标准语言名称（大小写不敏感）
        if language_clean == std_lang.lower():
            standard_language = std_lang
            alias_list = aliases
            break
        # 检查是否匹配别名（大小写不敏感）
        for alias in aliases:
            if language_clean == alias.lower():
                standard_language = std_lang
                alias_list = aliases
                break
        if standard_language:
            break

    if not standard_language:
        raise LanguageNotSupportedError(f"Language '{language}' is not supported")

    # 构建模板目录路径
    # 假设模板根目录为项目根目录下的 templates 目录

    # 获取项目根目录：当前文件所在目录的父目录
    project_root = Path(__file__).parent.parent
    template_root = project_root / "templates"
    template_dir = template_root / standard_language

    # 验证模板目录是否存在
    if not template_dir.exists() or not template_dir.is_dir():
        raise TemplateNotFoundError(f"Template directory not found: {template_dir}")

    # 返回 TemplateConfig
    return TemplateConfig(
        language=standard_language,
        alias=alias_list,
        template_dir=template_dir,
        required_files=REQUIRED_TEMPLATE_FILES.copy()  # 返回副本避免意外修改
    )


def validate_template(template_dir: Path) -> bool:
    """验证模板目录完整性

    Args:
        template_dir: 模板目录路径

    Returns:
        bool: 模板是否有效

    Raises:
        TemplateValidationError: 模板验证失败
    """
    from .constants import REQUIRED_TEMPLATE_FILES
    from .errors import TemplateValidationError

    # 验证输入
    if not template_dir.exists():
        raise TemplateValidationError(f"Template directory does not exist: {template_dir}")
    if not template_dir.is_dir():
        raise TemplateValidationError(f"Template path is not a directory: {template_dir}")

    missing_files = []
    for required_file in REQUIRED_TEMPLATE_FILES:
        file_path = template_dir / required_file
        if not file_path.exists():
            missing_files.append(required_file)
        elif not file_path.is_file():
            missing_files.append(f"{required_file} (not a regular file)")

    if missing_files:
        missing_list = ", ".join(missing_files)
        raise TemplateValidationError(
            f"Template validation failed. Missing required files: {missing_list}"
        )

    return True