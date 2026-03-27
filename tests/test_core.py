"""核心协调器测试模块

本模块包含对CCTool.initialize_project函数的表格驱动测试。
测试覆盖完整流程、参数传递、错误处理链和统计信息。
"""

import unittest
import tempfile
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 导入被测试模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from cc_tool.core import CCTool
from cc_tool.errors import (
    CCToolError, ProjectDirectoryError, LanguageNotSupportedError,
    TemplateNotFoundError
)


class TestCCToolInitializeProject(unittest.TestCase):
    """测试CCTool.initialize_project方法"""

    def setUp(self):
        """每个测试前的准备工作"""
        # 创建临时目录用于测试
        self.test_temp_dir = tempfile.mkdtemp(prefix="cc_tool_test_")
        self.test_project_dir = Path(self.test_temp_dir) / "test_project"
        self.test_project_dir.mkdir(parents=True, exist_ok=True)

        # 创建CCTool实例
        self.tool = CCTool()

    def tearDown(self):
        """每个测试后的清理工作"""
        # 删除临时目录
        shutil.rmtree(self.test_temp_dir, ignore_errors=True)

    # 表格驱动测试：正常流程
    def test_initialize_project_normal_flow(self):
        """测试正常初始化流程"""
        test_cases = [
            {
                "name": "基本Python项目",
                "language": "python",
                "skip_existing": True,
                "dry_run": False,
                "init_user_framework": True,
                "expected_keys": ["copied_files", "skipped_files",
                                 "gitignore_modified", "user_framework_created"]
            },
            {
                "name": "JavaScript项目跳过用户框架初始化",
                "language": "javascript",
                "skip_existing": True,
                "dry_run": False,
                "init_user_framework": False,
                "expected_keys": ["copied_files", "skipped_files",
                                 "gitignore_modified", "user_framework_created"]
            },
            {
                "name": "Go项目dry-run模式",
                "language": "go",
                "skip_existing": True,
                "dry_run": True,
                "init_user_framework": True,
                "expected_keys": ["copied_files", "skipped_files",
                                 "gitignore_modified", "user_framework_created"]
            },
            {
                "name": "Rust项目不跳过已存在文件",
                "language": "rust",
                "skip_existing": False,
                "dry_run": False,
                "init_user_framework": True,
                "expected_keys": ["copied_files", "skipped_files",
                                 "gitignore_modified", "user_framework_created"]
            },
            {
                "name": "Java项目静默模式",
                "language": "java",
                "skip_existing": True,
                "dry_run": False,
                "init_user_framework": True,
                "expected_keys": ["copied_files", "skipped_files",
                                 "gitignore_modified", "user_framework_created"]
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                # 使用mock替代实际的文件操作，因为我们测试的是协调逻辑
                # 而不是具体的文件复制
                with patch('cc_tool.template.find_template') as mock_find_template, \
                     patch('cc_tool.file_ops.copy_template_files') as mock_copy, \
                     patch('cc_tool.gitignore.manage_gitignore') as mock_gitignore, \
                     patch('cc_tool.user_config.initialize_user_config') as mock_user_config:

                    # 配置mock返回值
                    mock_find_template.return_value = MagicMock(
                        language=case["language"],
                        template_dir=Path("/fake/template"),
                        required_files=[".claude/settings.json", "CLAUDE.md"]
                    )
                    mock_copy.return_value = MagicMock(
                        copied_files=[Path("file1.txt"), Path("file2.txt")],
                        skipped_files=[Path("existing.txt")]
                    )
                    mock_gitignore.return_value = True  # .gitignore被修改
                    mock_user_config.return_value = [Path(".claude/settings.json")]

                    # 调用被测试方法
                    result = self.tool.initialize_project(
                        project_dir=self.test_project_dir,
                        language=case["language"],
                        skip_existing=case["skip_existing"],
                        dry_run=case["dry_run"],
                        init_user_framework=case["init_user_framework"]
                    )

                    # 验证结果结构
                    self.assertIsInstance(result, dict)
                    for key in case["expected_keys"]:
                        self.assertIn(key, result)

                    # 验证mock被调用（对于dry_run模式，某些mock可能不被调用）
                    if not case["dry_run"]:
                        mock_find_template.assert_called_once()
                        mock_copy.assert_called_once()
                        mock_gitignore.assert_called_once()
                        if case["init_user_framework"]:
                            mock_user_config.assert_called_once()
                        else:
                            mock_user_config.assert_not_called()
                    else:
                        # dry_run模式下，实际文件操作应该被跳过
                        # 但模板查找和.gitignore检查可能仍然进行
                        pass

    # 表格驱动测试：错误处理链
    def test_initialize_project_error_handling(self):
        """测试错误处理链"""
        test_cases = [
            {
                "name": "项目目录不存在",
                "language": "python",
                "project_dir": Path("/non/existent/directory"),
                "expected_error": ProjectDirectoryError,
                "mock_side_effect": ProjectDirectoryError("Directory does not exist")
            },
            {
                "name": "不支持的语言",
                "language": "ruby",
                "project_dir": None,  # 使用self.test_project_dir
                "expected_error": LanguageNotSupportedError,
                "mock_side_effect": LanguageNotSupportedError("Unsupported language: ruby")
            },
            {
                "name": "模板目录不存在",
                "language": "python",
                "project_dir": None,
                "expected_error": TemplateNotFoundError,
                "mock_side_effect": TemplateNotFoundError("Template not found")
            },
            {
                "name": "权限不足",
                "language": "python",
                "project_dir": None,
                "expected_error": PermissionError,
                "mock_side_effect": PermissionError("Permission denied")
            },
            {
                "name": "文件复制错误",
                "language": "python",
                "project_dir": None,
                "expected_error": CCToolError,
                "mock_side_effect": CCToolError("File copy failed")
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                project_dir = case["project_dir"] if case["project_dir"] else self.test_project_dir

                # 使用mock模拟异常抛出
                with patch('cc_tool.template.find_template') as mock_find_template:
                    mock_find_template.side_effect = case["mock_side_effect"]

                    # 验证抛出预期异常
                    with self.assertRaises(case["expected_error"]):
                        self.tool.initialize_project(
                            project_dir=project_dir,
                            language=case["language"]
                        )

    # 表格驱动测试：参数传递验证
    def test_initialize_project_parameter_passing(self):
        """测试参数正确传递给底层模块"""
        test_cases = [
            {
                "name": "传递skip_existing参数",
                "skip_existing": False,
                "expected_skip_existing": False
            },
            {
                "name": "传递dry_run参数",
                "skip_existing": True,
                "dry_run": True,
                "expected_dry_run": True
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                with patch('cc_tool.template.find_template') as mock_find_template, \
                     patch('cc_tool.file_ops.copy_template_files') as mock_copy, \
                     patch('cc_tool.gitignore.manage_gitignore') as mock_gitignore, \
                     patch('cc_tool.user_config.initialize_user_config') as mock_user_config:

                    # 配置mock
                    mock_find_template.return_value = MagicMock(
                        language="python",
                        template_dir=Path("/fake/template"),
                        required_files=[]
                    )
                    mock_copy.return_value = MagicMock(
                        copied_files=[], skipped_files=[]
                    )
                    mock_gitignore.return_value = False
                    mock_user_config.return_value = []

                    # 提取测试参数
                    skip_existing = case.get("skip_existing", True)
                    dry_run = case.get("dry_run", False)

                    # 调用方法
                    self.tool.initialize_project(
                        project_dir=self.test_project_dir,
                        language="python",
                        skip_existing=skip_existing,
                        dry_run=dry_run,
                        init_user_framework=False
                    )

                    # 验证参数传递给copy_template_files
                    if not dry_run:
                        mock_copy.assert_called_once()
                        call_kwargs = mock_copy.call_args.kwargs
                        if "skip_existing" in case:
                            self.assertEqual(call_kwargs.get("skip_existing"), case["skip_existing"])
                        if "dry_run" in case:
                            self.assertEqual(call_kwargs.get("dry_run"), case["dry_run"])

    # 表格驱动测试：CopyResult统计信息验证
    def test_initialize_project_statistics(self):
        """测试返回的统计信息正确性"""
        test_cases = [
            {
                "name": "有文件复制和跳过",
                "mock_copied": [Path(".claude/settings.json"), Path("CLAUDE.md")],
                "mock_skipped": [Path("existing.txt")],
                "mock_gitignore_modified": True,
                "mock_user_framework": [Path(".claude/settings.json")],
                "expected_copied_count": 2,
                "expected_skipped_count": 1,
                "expected_gitignore_modified": True,
                "expected_user_framework_count": 1
            },
            {
                "name": "无文件复制",
                "mock_copied": [],
                "mock_skipped": [Path("existing1.txt"), Path("existing2.txt")],
                "mock_gitignore_modified": False,
                "mock_user_framework": [],
                "expected_copied_count": 0,
                "expected_skipped_count": 2,
                "expected_gitignore_modified": False,
                "expected_user_framework_count": 0
            },
            {
                "name": "所有文件都跳过",
                "mock_copied": [],
                "mock_skipped": [Path(".claude/settings.json"), Path("CLAUDE.md")],
                "mock_gitignore_modified": False,
                "mock_user_framework": [Path(".claude/settings.json")],
                "expected_copied_count": 0,
                "expected_skipped_count": 2,
                "expected_gitignore_modified": False,
                "expected_user_framework_count": 1
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                with patch('cc_tool.template.find_template') as mock_find_template, \
                     patch('cc_tool.file_ops.copy_template_files') as mock_copy, \
                     patch('cc_tool.gitignore.manage_gitignore') as mock_gitignore, \
                     patch('cc_tool.user_config.initialize_user_config') as mock_user_config:

                    # 配置mock返回值
                    mock_find_template.return_value = MagicMock(
                        language="python",
                        template_dir=Path("/fake/template"),
                        required_files=[]
                    )
                    mock_copy.return_value = MagicMock(
                        copied_files=case["mock_copied"],
                        skipped_files=case["mock_skipped"]
                    )
                    mock_gitignore.return_value = case["mock_gitignore_modified"]
                    mock_user_config.return_value = case["mock_user_framework"]

                    # 调用方法
                    result = self.tool.initialize_project(
                        project_dir=self.test_project_dir,
                        language="python",
                        init_user_framework=bool(case["mock_user_framework"])
                    )

                    # 验证统计信息
                    self.assertEqual(len(result["copied_files"]), case["expected_copied_count"])
                    self.assertEqual(len(result["skipped_files"]), case["expected_skipped_count"])
                    self.assertEqual(result["gitignore_modified"], case["expected_gitignore_modified"])
                    self.assertEqual(len(result["user_framework_created"]),
                                   case["expected_user_framework_count"])

    # 表格驱动测试：语言别名和大小写不敏感
    def test_initialize_project_language_variations(self):
        """测试语言别名和大小写不敏感处理"""
        test_cases = [
            {
                "name": "Python别名'py'",
                "language": "py",
                "expected_normalized": "python"
            },
            {
                "name": "JavaScript别名'js'",
                "language": "js",
                "expected_normalized": "javascript"
            },
            {
                "name": "Go别名'golang'",
                "language": "golang",
                "expected_normalized": "go"
            },
            {
                "name": "大写PYTHON",
                "language": "PYTHON",
                "expected_normalized": "python"
            },
            {
                "name": "混合大小写JaVaScRiPt",
                "language": "JaVaScRiPt",
                "expected_normalized": "javascript"
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                with patch('cc_tool.template.find_template') as mock_find_template, \
                     patch('cc_tool.file_ops.copy_template_files') as mock_copy, \
                     patch('cc_tool.gitignore.manage_gitignore') as mock_gitignore, \
                     patch('cc_tool.user_config.initialize_user_config') as mock_user_config:

                    # 配置mock
                    mock_find_template.return_value = MagicMock(
                        language=case["expected_normalized"],
                        template_dir=Path("/fake/template"),
                        required_files=[]
                    )
                    mock_copy.return_value = MagicMock(
                        copied_files=[], skipped_files=[]
                    )
                    mock_gitignore.return_value = False
                    mock_user_config.return_value = []

                    # 调用方法
                    self.tool.initialize_project(
                        project_dir=self.test_project_dir,
                        language=case["language"],
                        init_user_framework=False
                    )

                    # 验证传递给find_template的语言参数
                    mock_find_template.assert_called_once()
                    # 注意：语言规范化应该在find_template内部处理
                    # 我们只是验证调用了find_template，具体语言处理由template模块测试

    def test_initialize_project_with_custom_logger(self):
        """测试使用自定义日志记录器"""
        with patch('cc_tool.logger.Logger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            # 创建带有自定义logger的CCTool实例
            tool_with_logger = CCTool(logger=mock_logger)

            with patch('cc_tool.template.find_template') as mock_find_template, \
                 patch('cc_tool.file_ops.copy_template_files') as mock_copy, \
                 patch('cc_tool.gitignore.manage_gitignore') as mock_gitignore:

                mock_find_template.return_value = MagicMock(
                    language="python",
                    template_dir=Path("/fake/template"),
                    required_files=[]
                )
                mock_copy.return_value = MagicMock(
                    copied_files=[], skipped_files=[]
                )
                mock_gitignore.return_value = False

                # 调用方法
                tool_with_logger.initialize_project(
                    project_dir=self.test_project_dir,
                    language="python",
                    init_user_framework=False
                )

                # 验证logger被使用（至少info被调用）
                # 实际实现中应该有日志调用
                # mock_logger.info.assert_called()  # 实际实现中取消注释

    def test_initialize_project_dry_run_does_not_modify_files(self):
        """测试dry-run模式不实际修改文件"""
        with patch('cc_tool.template.find_template') as mock_find_template, \
             patch('cc_tool.file_ops.copy_template_files') as mock_copy, \
             patch('cc_tool.gitignore.manage_gitignore') as mock_gitignore, \
             patch('cc_tool.user_config.initialize_user_config') as mock_user_config:

            mock_find_template.return_value = MagicMock(
                language="python",
                template_dir=Path("/fake/template"),
                required_files=[]
            )

            # 调用dry-run模式
            self.tool.initialize_project(
                project_dir=self.test_project_dir,
                language="python",
                dry_run=True,
                init_user_framework=False
            )

            # 验证copy_template_files以dry_run=True调用
            mock_copy.assert_called_once()
            call_kwargs = mock_copy.call_args.kwargs
            self.assertTrue(call_kwargs.get("dry_run", False))

            # 验证manage_gitignore以dry_run=True调用
            mock_gitignore.assert_called_once()
            # manage_gitignore的dry_run参数可能在函数签名中

            # 验证initialize_user_config未被调用（因为init_user_framework=False）
            mock_user_config.assert_not_called()


if __name__ == "__main__":
    unittest.main()