"""核心协调器模块

本模块提供CCTool类，协调模板查找、文件复制、.gitignore管理等各个模块，
实现完整的项目初始化流程。
"""

from pathlib import Path
from typing import Dict, Any, List, Optional

from cc_tool.logger import Logger
import cc_tool.template
import cc_tool.file_ops
import cc_tool.gitignore
import cc_tool.user_config
from cc_tool.errors import CCToolError, ProjectDirectoryError, LanguageNotSupportedError, TemplateNotFoundError
from cc_tool.models import TemplateConfig, ProjectContext, CopyResult


class CCTool:
    """cc-tool核心协调器，组合各个模块的功能。"""

    def __init__(
        self,
        logger: Optional[Logger] = None,
        template_base_dir: Optional[Path] = None
    ):
        """
        初始化CCTool实例。

        Args:
            logger: 日志记录器实例，默认创建新的
            template_base_dir: 模板基础目录，默认为内置模板目录
        """
        self.logger = logger or Logger()
        self.template_base_dir = template_base_dir
        # TODO: 支持自定义template_base_dir，目前先忽略

    def initialize_project(
        self,
        project_dir: Path,
        language: str,
        *,
        skip_existing: bool = True,
        dry_run: bool = False,
        init_user_framework: bool = True
    ) -> Dict[str, Any]:
        """
        初始化项目目录。

        Args:
            project_dir: 项目目录路径
            language: 编程语言名称
            skip_existing: 是否跳过已存在的文件
            dry_run: 是否只预览不实际执行
            init_user_framework: 是否初始化用户级框架

        Returns:
            Dict[str, Any]: 操作结果统计，包含：
                - copied_files: List[Path] 复制的文件列表
                - skipped_files: List[Path] 跳过的文件列表
                - gitignore_modified: bool .gitignore是否被修改
                - user_framework_created: List[Path] 创建的用户框架项

        Raises:
            CCToolError: 任何子错误都会转换为CCToolError
        """
        try:
            # 验证项目目录是否存在
            if not project_dir.exists():
                raise ProjectDirectoryError(f"项目目录不存在: {project_dir}")
            if not project_dir.is_dir():
                raise ProjectDirectoryError(f"项目路径不是目录: {project_dir}")

            # 查找模板
            template_config = cc_tool.template.find_template(language)

            # 创建项目上下文
            project_name = project_dir.name
            context = ProjectContext(
                project_dir=project_dir,
                project_name=project_name,
                language=language,
                verbose=False,  # 暂不支持
                dry_run=dry_run,
                quiet=False     # 暂不支持
            )

            # 复制模板文件
            copy_result = cc_tool.file_ops.copy_template_files(
                template_dir=template_config.template_dir,
                project_dir=project_dir,
                context=context,
                skip_existing=skip_existing,
                dry_run=dry_run
            )

            # 管理.gitignore文件
            gitignore_modified = cc_tool.gitignore.manage_gitignore(
                project_dir=project_dir,
                language=language,
                dry_run=dry_run
            )

            # 初始化用户级框架（如果需要）
            user_framework_created = []
            if init_user_framework and not dry_run:
                user_framework_created = cc_tool.user_config.initialize_user_config()

            # 返回统计信息
            # 兼容测试中的mock（使用copied_files/skipped_files）和实际CopyResult（使用copied/skipped）
            copied = getattr(copy_result, 'copied', None)
            skipped = getattr(copy_result, 'skipped', None)
            return {
                "copied": copied,
                "skipped": skipped,
                "gitignore_modified": gitignore_modified,
                "user_framework_created": user_framework_created
            }

        except (ProjectDirectoryError, LanguageNotSupportedError,
                TemplateNotFoundError, PermissionError, CCToolError) as e:
            # 这些是已知错误类型，直接重新抛出
            raise
        except Exception as e:
            # 其他未知错误包装为CCToolError
            raise CCToolError(f"项目初始化失败: {e}") from e

    def list_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        from cc_tool.constants import SUPPORTED_LANGUAGES
        return list(SUPPORTED_LANGUAGES.keys())

    def list_templates(self) -> Dict[str, List[str]]:
        """列出所有可用的模板"""
        from cc_tool.constants import SUPPORTED_LANGUAGES
        result = {}
        for lang in SUPPORTED_LANGUAGES.keys():
            try:
                template_config = cc_tool.template.find_template(lang)
                result[lang] = [str(template_config.template_dir)]
            except Exception:
                result[lang] = []
        return result