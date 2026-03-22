"""命令行接口测试模块

本模块包含对cc-tool命令行参数解析的表格驱动测试。
测试覆盖必需参数验证、非法参数检测等场景。
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import sys

# 导入被测试模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from cc_tool.cli import parse_args
from cc_tool.errors import LanguageNotSupportedError, ProjectDirectoryError


class TestCLIParseArgs(unittest.TestCase):
    """测试命令行参数解析"""

    def setUp(self):
        """每个测试前的准备工作"""
        # 创建一个临时目录作为有效的项目目录
        self.temp_dir = tempfile.mkdtemp()
        self.valid_project_dir = Path(self.temp_dir) / "myproject"
        self.valid_project_dir.mkdir()

    def tearDown(self):
        """每个测试后的清理工作"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 表格驱动测试：正常用例
    def test_valid_arguments(self):
        """测试有效的命令行参数"""
        test_cases = [
            {
                "name": "标准语言名称",
                "args": [str(self.valid_project_dir), "python"],
                "expected_language": "python",
            },
            {
                "name": "语言别名（小写）",
                "args": [str(self.valid_project_dir), "py"],
                "expected_language": "python",
            },
            {
                "name": "语言别名（大写）",
                "args": [str(self.valid_project_dir), "PY"],
                "expected_language": "python",
            },
            {
                "name": "JavaScript语言",
                "args": [str(self.valid_project_dir), "javascript"],
                "expected_language": "javascript",
            },
            {
                "name": "TypeScript别名",
                "args": [str(self.valid_project_dir), "typescript"],
                "expected_language": "javascript",
            },
            {
                "name": "Go语言",
                "args": [str(self.valid_project_dir), "go"],
                "expected_language": "go",
            },
            {
                "name": "Rust语言",
                "args": [str(self.valid_project_dir), "rust"],
                "expected_language": "rust",
            },
            {
                "name": "Java语言",
                "args": [str(self.valid_project_dir), "java"],
                "expected_language": "java",
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                args = parse_args(case["args"])
                self.assertEqual(str(args.project_dir), str(self.valid_project_dir))
                self.assertEqual(args.language, case["expected_language"])  # 标准化后的语言

    # 表格驱动测试：缺失必需参数
    def test_missing_required_arguments(self):
        """测试缺失必需参数"""
        test_cases = [
            {
                "name": "缺失项目目录",
                "args": ["python"],
                "expected_error": SystemExit,  # argparse 默认行为
            },
            {
                "name": "缺失语言参数",
                "args": [str(self.valid_project_dir)],
                "expected_error": SystemExit,
            },
            {
                "name": "两个参数都缺失",
                "args": [],
                "expected_error": SystemExit,
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                with self.assertRaises(case["expected_error"]):
                    parse_args(case["args"])

    # 表格驱动测试：非法语言参数
    def test_invalid_language(self):
        """测试不支持的语言"""
        test_cases = [
            {
                "name": "完全不支持的语言",
                "args": [str(self.valid_project_dir), "ruby"],
                "expected_error": LanguageNotSupportedError,
            },
            {
                "name": "空字符串",
                "args": [str(self.valid_project_dir), ""],
                "expected_error": LanguageNotSupportedError,
            },
            {
                "name": "仅空白字符",
                "args": [str(self.valid_project_dir), "   "],
                "expected_error": LanguageNotSupportedError,
            },
            {
                "name": "数字",
                "args": [str(self.valid_project_dir), "123"],
                "expected_error": LanguageNotSupportedError,
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                # 当前 parse_args 不会验证语言，因此不会抛出 LanguageNotSupportedError
                # 这个测试应该失败，因为预期的异常没有被抛出
                with self.assertRaises(case["expected_error"]):
                    parse_args(case["args"])

    # 表格驱动测试：非法项目目录
    def test_invalid_project_directory(self):
        """测试无效的项目目录"""
        # 创建一个不可写的目录（需要root权限，难以模拟）
        # 使用不存在的父目录作为无效路径
        invalid_dir = Path("/nonexistent/path/to/project")

        test_cases = [
            {
                "name": "不存在的目录",
                "args": [str(invalid_dir), "python"],
                "expected_error": ProjectDirectoryError,
            },
            {
                "name": "文件而非目录",
                "args": [__file__, "python"],  # 使用当前测试文件作为路径
                "expected_error": ProjectDirectoryError,
            },
            {
                "name": "空字符串",
                "args": ["", "python"],
                "expected_error": SystemExit,
            },
            {
                "name": "仅空白字符",
                "args": ["   ", "python"],
                "expected_error": ProjectDirectoryError,
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                # 当前 parse_args 不会验证项目目录，因此不会抛出 ProjectDirectoryError
                # 这个测试应该失败，因为预期的异常没有被抛出
                with self.assertRaises(case["expected_error"]):
                    parse_args(case["args"])

    # 测试可选参数
    def test_optional_arguments(self):
        """测试可选参数解析"""
        test_cases = [
            {
                "name": "详细模式",
                "args": [str(self.valid_project_dir), "python", "--verbose"],
                "expected_verbose": True,
                "expected_dry_run": False,
                "expected_quiet": False,
            },
            {
                "name": "简短详细模式",
                "args": [str(self.valid_project_dir), "python", "-V"],
                "expected_verbose": True,
                "expected_dry_run": False,
                "expected_quiet": False,
            },
            {
                "name": "预览模式",
                "args": [str(self.valid_project_dir), "python", "--dry-run"],
                "expected_verbose": False,
                "expected_dry_run": True,
                "expected_quiet": False,
            },
            {
                "name": "简短预览模式",
                "args": [str(self.valid_project_dir), "python", "-n"],
                "expected_verbose": False,
                "expected_dry_run": True,
                "expected_quiet": False,
            },
            {
                "name": "静默模式",
                "args": [str(self.valid_project_dir), "python", "--quiet"],
                "expected_verbose": False,
                "expected_dry_run": False,
                "expected_quiet": True,
            },
            {
                "name": "简短静默模式",
                "args": [str(self.valid_project_dir), "python", "-q"],
                "expected_verbose": False,
                "expected_dry_run": False,
                "expected_quiet": True,
            },
            {
                "name": "组合模式",
                "args": [str(self.valid_project_dir), "python", "--verbose", "--dry-run", "--quiet"],
                "expected_verbose": True,
                "expected_dry_run": True,
                "expected_quiet": True,
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                args = parse_args(case["args"])
                self.assertEqual(args.verbose, case["expected_verbose"])
                self.assertEqual(args.dry_run, case["expected_dry_run"])
                self.assertEqual(args.quiet, case["expected_quiet"])

    def test_list_languages_flag(self):
        """测试 --list-languages 标志"""
        # 当使用 --list-languages 时，应该不需要其他参数
        # 但当前实现中，argparse 仍然需要必需参数
        # 这个测试应该失败，因为我们的实现尚未正确处理这个标志
        with self.assertRaises(SystemExit):
            parse_args(["--list-languages"])

    def test_list_templates_flag(self):
        """测试 --list-templates 标志"""
        with self.assertRaises(SystemExit):
            parse_args(["--list-templates"])

    def test_version_flag(self):
        """测试 --version 标志"""
        with self.assertRaises(SystemExit):  # argparse 的 version 动作会退出
            parse_args(["--version"])


if __name__ == "__main__":
    unittest.main()