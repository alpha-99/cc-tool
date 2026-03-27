"""文件操作测试模块

本模块包含对文件变量替换功能的表格驱动测试。
测试覆盖变量替换、边界条件、异常处理等场景。
"""

import unittest
import tempfile
import shutil
import sys
from pathlib import Path

# 导入被测试模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from cc_tool.file_ops import replace_variables_in_file, copy_template_files
from cc_tool.errors import VariableReplaceError
from cc_tool.models import ProjectContext, CopyResult


class TestReplaceVariablesInFile(unittest.TestCase):
    """测试文件变量替换功能"""

    def setUp(self):
        """每个测试前的准备工作"""
        self.temp_dir = Path(tempfile.mkdtemp())
        # 创建测试用的 ProjectContext
        self.context = ProjectContext(
            project_dir=self.temp_dir / "myproject",
            project_name="MyProject",
            language="python",
            verbose=False,
            dry_run=False,
            quiet=False,
        )

    def tearDown(self):
        """每个测试后的清理工作"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 表格驱动测试：正常用例 - 单个变量替换
    def test_replace_single_variable(self):
        """测试替换单个变量"""
        test_cases = [
            {
                "name": "替换 PROJECT_NAME",
                "template_content": "项目名称: {{PROJECT_NAME}}",
                "expected_content": "项目名称: MyProject",
            },
            {
                "name": "替换 LANGUAGE",
                "template_content": "语言: {{LANGUAGE}}",
                "expected_content": "语言: python",
            },
            {
                "name": "替换 PROJECT_DIR",
                "template_content": "项目目录: {{PROJECT_DIR}}",
                "expected_content": f"项目目录: {self.context.project_dir}",
            },
            {
                "name": "多行文本中的变量",
                "template_content": "第一行\n第二行: {{PROJECT_NAME}}\n第三行: {{LANGUAGE}}",
                "expected_content": f"第一行\n第二行: MyProject\n第三行: python",
            },
            {
                "name": "行内多个变量",
                "template_content": "项目: {{PROJECT_NAME}} ({{LANGUAGE}})",
                "expected_content": "项目: MyProject (python)",
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                # 创建测试文件
                test_file = self.temp_dir / "test.txt"
                test_file.write_text(case["template_content"], encoding="utf-8")

                # 调用函数替换变量
                replace_variables_in_file(test_file, self.context)
                # 验证文件内容
                actual_content = test_file.read_text(encoding="utf-8")
                self.assertEqual(actual_content, case["expected_content"])

    # 表格驱动测试：多个变量替换
    def test_replace_multiple_variables(self):
        """测试替换多个不同的变量"""
        test_cases = [
            {
                "name": "所有支持的变量",
                "template_content": """项目名称: {{PROJECT_NAME}}
语言: {{LANGUAGE}}
目录: {{PROJECT_DIR}}""",
                "expected_content": f"""项目名称: MyProject
语言: python
目录: {self.context.project_dir}""",
            },
            {
                "name": "变量重复出现",
                "template_content": "{{PROJECT_NAME}} - {{PROJECT_NAME}} - {{PROJECT_NAME}}",
                "expected_content": "MyProject - MyProject - MyProject",
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                test_file = self.temp_dir / "test.txt"
                test_file.write_text(case["template_content"], encoding="utf-8")

                replace_variables_in_file(test_file, self.context)
                actual_content = test_file.read_text(encoding="utf-8")
                self.assertEqual(actual_content, case["expected_content"])

    # 表格驱动测试：边界条件
    def test_replace_variable_edge_cases(self):
        """测试变量替换的边界条件"""
        test_cases = [
            {
                "name": "空文件",
                "template_content": "",
                "expected_content": "",
            },
            {
                "name": "只有空白字符",
                "template_content": "   \n\t\n  ",
                "expected_content": "   \n\t\n  ",
            },
            {
                "name": "没有变量占位符",
                "template_content": "这是普通文本，没有变量。",
                "expected_content": "这是普通文本，没有变量。",
            },
            {
                "name": "变量占位符前后有空格",
                "template_content": "项目: {{ PROJECT_NAME }}",
                "expected_content": "项目: {{ PROJECT_NAME }}",  # 注意：空格可能导致不匹配
            },
            {
                "name": "不完整的占位符",
                "template_content": "项目: {{PROJECT_NAME",
                "expected_content": "项目: {{PROJECT_NAME",
            },
            {
                "name": "错误的括号",
                "template_content": "项目: {PROJECT_NAME}}",
                "expected_content": "项目: {PROJECT_NAME}}",
            },
            {
                "name": "嵌套占位符",
                "template_content": "项目: {{ {{PROJECT_NAME}} }}",
                "expected_content": "项目: {{ MyProject }}",  # 可能替换内层占位符
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                test_file = self.temp_dir / "test.txt"
                test_file.write_text(case["template_content"], encoding="utf-8")

                replace_variables_in_file(test_file, self.context)
                actual_content = test_file.read_text(encoding="utf-8")
                self.assertEqual(actual_content, case["expected_content"])

    # 表格驱动测试：不支持的变量
    def test_replace_unsupported_variable(self):
        """测试替换不支持的变量"""
        test_cases = [
            {
                "name": "不存在的变量",
                "template_content": "变量: {{UNKNOWN_VARIABLE}}",
                "expected_content": "变量: {{UNKNOWN_VARIABLE}}",  # 应保持不变
            },
            {
                "name": "小写变量名",
                "template_content": "变量: {{project_name}}",
                "expected_content": "变量: {{project_name}}",  # 模式要求大写
            },
            {
                "name": "混合大小写",
                "template_content": "变量: {{Project_Name}}",
                "expected_content": "变量: {{Project_Name}}",
            },
            {
                "name": "带下划线的非标准变量",
                "template_content": "变量: {{PROJECT_NAME_EXTRA}}",
                "expected_content": "变量: {{PROJECT_NAME_EXTRA}}",
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                test_file = self.temp_dir / "test.txt"
                test_file.write_text(case["template_content"], encoding="utf-8")

                replace_variables_in_file(test_file, self.context)
                actual_content = test_file.read_text(encoding="utf-8")
                self.assertEqual(actual_content, case["expected_content"])

    # 表格驱动测试：异常情况
    def test_replace_variables_exceptions(self):
        """测试变量替换的异常情况"""
        test_cases = [
            {
                "name": "文件不存在",
                "file_path": self.temp_dir / "nonexistent.txt",
                "expected_error": VariableReplaceError,  # 或 FileNotFoundError
            },
            {
                "name": "目录而非文件",
                "file_path": self.temp_dir,
                "expected_error": VariableReplaceError,
            },
            {
                "name": "无读取权限",
                "file_path": None,  # 需要特殊设置
                "expected_error": VariableReplaceError,
            },
            {
                "name": "无写入权限",
                "file_path": None,  # 需要特殊设置
                "expected_error": VariableReplaceError,
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                # 设置测试文件
                if case["file_path"] is not None and case["name"] != "文件不存在":
                    case["file_path"].touch()

                # 跳过需要特殊权限的测试（file_path为None）
                if case["file_path"] is None:
                    self.skipTest("需要特殊权限的测试已跳过")
                    continue

                with self.assertRaises(case["expected_error"]):
                    replace_variables_in_file(case["file_path"], self.context)

    # 表格驱动测试：不同文件编码
    def test_replace_variables_file_encoding(self):
        """测试不同文件编码的变量替换"""
        test_cases = [
            {
                "name": "UTF-8 编码",
                "encoding": "utf-8",
                "template_content": "项目: {{PROJECT_NAME}} - 中文测试",
                "expected_content": "项目: MyProject - 中文测试",
            },
            {
                "name": "UTF-8 with BOM",
                "encoding": "utf-8-sig",
                "template_content": "项目: {{PROJECT_NAME}}",
                "expected_content": "项目: MyProject",
            },
            # 注意：可能不支持非UTF编码，但这是实现细节
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                test_file = self.temp_dir / "test.txt"
                test_file.write_text(case["template_content"], encoding=case["encoding"])

                replace_variables_in_file(test_file, self.context)
                actual_content = test_file.read_text(encoding=case["encoding"])
                self.assertEqual(actual_content, case["expected_content"])

    def test_replace_variables_preserves_other_content(self):
        """验证变量替换不影响其他内容"""
        template = """# 项目配置文件
PROJECT_NAME = "{{PROJECT_NAME}}"
LANGUAGE = "{{LANGUAGE}}"

# 其他配置
DEBUG = True
PORT = 8080

# 项目描述
这是一个{{LANGUAGE}}项目，名为{{PROJECT_NAME}}。"""

        expected = f"""# 项目配置文件
PROJECT_NAME = "MyProject"
LANGUAGE = "python"

# 其他配置
DEBUG = True
PORT = 8080

# 项目描述
这是一个python项目，名为MyProject。"""

        test_file = self.temp_dir / "config.py"
        test_file.write_text(template, encoding="utf-8")

        replace_variables_in_file(test_file, self.context)
        actual_content = test_file.read_text(encoding="utf-8")
        self.assertEqual(actual_content, expected)


class TestCopyTemplateFiles(unittest.TestCase):
    """测试模板文件复制功能"""

    def setUp(self):
        """每个测试前的准备工作"""
        import tempfile
        self.temp_dir = Path(tempfile.mkdtemp())
        # 创建测试用的 ProjectContext
        self.context = ProjectContext(
            project_dir=self.temp_dir / "myproject",
            project_name="MyProject",
            language="python",
            verbose=False,
            dry_run=False,
            quiet=False,
        )

    def tearDown(self):
        """每个测试后的清理工作"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_copy_template_files_basic(self):
        """测试基本文件复制行为"""
        test_cases = [
            {
                "name": "复制新文件",
                "template_files": [".claude/settings.json"],
                "existing_files": [],
                "expected_copied": [".claude/settings.json"],
                "expected_skipped": [],
            },
            {
                "name": "跳过已存在文件",
                "template_files": ["CLAUDE.md"],
                "existing_files": ["CLAUDE.md"],
                "expected_copied": [],
                "expected_skipped": ["CLAUDE.md"],
            },
            {
                "name": "混合情况",
                "template_files": [".claude/settings.json", "CLAUDE.md", "constitution.md"],
                "existing_files": ["CLAUDE.md"],
                "expected_copied": [".claude/settings.json", "constitution.md"],
                "expected_skipped": ["CLAUDE.md"],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                # 创建模板目录结构
                template_dir = self.temp_dir / f"template_{case['name']}"
                template_dir.mkdir(exist_ok=True)
                for file_rel in case["template_files"]:
                    file_path = template_dir / file_rel
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(f"Content of {file_rel}", encoding="utf-8")

                # 创建项目目录结构（已存在文件）
                project_dir = self.temp_dir / f"project_{case['name']}"
                project_dir.mkdir(exist_ok=True)
                for file_rel in case["existing_files"]:
                    file_path = project_dir / file_rel
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(f"Existing content of {file_rel}", encoding="utf-8")

                # 调用复制函数
                result = copy_template_files(template_dir, project_dir, self.context)

                # 验证复制结果
                copied_rel = [str(p.relative_to(project_dir)) for p in result.copied]
                skipped_rel = [str(p.relative_to(project_dir)) for p in result.skipped]
                self.assertEqual(set(copied_rel), set(case["expected_copied"]))
                self.assertEqual(set(skipped_rel), set(case["expected_skipped"]))
                self.assertEqual(len(result.errors), 0)

                # 验证文件内容
                for file_rel in case["expected_copied"]:
                    expected_content = f"Content of {file_rel}"
                    actual_content = (project_dir / file_rel).read_text(encoding="utf-8")
                    self.assertEqual(actual_content, expected_content)

    def test_copy_template_files_recursive(self):
        """测试递归复制和目录创建"""
        test_cases = [
            {
                "name": "嵌套目录结构",
                "template_files": [
                    ".claude/settings.json",
                    ".claude/agents/empty.txt",
                    "specs/readme.md",
                    "specs/requirements.txt",
                ],
                "existing_files": [],
                "expected_copied": [
                    ".claude/settings.json",
                    ".claude/agents/empty.txt",
                    "specs/readme.md",
                    "specs/requirements.txt",
                ],
                "expected_skipped": [],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                template_dir = self.temp_dir / "template"
                template_dir.mkdir()
                for file_rel in case["template_files"]:
                    file_path = template_dir / file_rel
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(f"Content of {file_rel}", encoding="utf-8")

                project_dir = self.temp_dir / "project"
                project_dir.mkdir()

                result = copy_template_files(template_dir, project_dir, self.context)

                copied_rel = [str(p.relative_to(project_dir)) for p in result.copied]
                self.assertEqual(set(copied_rel), set(case["expected_copied"]))
                self.assertEqual(len(result.skipped), 0)
                self.assertEqual(len(result.errors), 0)

                # 验证所有文件都存在
                for file_rel in case["expected_copied"]:
                    self.assertTrue((project_dir / file_rel).exists())

    def test_copy_template_files_dry_run(self):
        """测试dry-run预览模式"""
        template_dir = self.temp_dir / "template"
        template_dir.mkdir()
        (template_dir / "test.txt").write_text("Content", encoding="utf-8")

        project_dir = self.temp_dir / "project"
        project_dir.mkdir()

        # dry_run=True 应该不实际复制文件
        result = copy_template_files(template_dir, project_dir, self.context, dry_run=True)

        # 验证结果统计
        self.assertEqual(len(result.copied), 1)
        self.assertEqual(len(result.skipped), 0)
        self.assertEqual(len(result.errors), 0)

        # 验证文件未被实际复制
        self.assertFalse((project_dir / "test.txt").exists())

    def test_copy_template_files_symlink(self):
        """测试符号链接处理（应作为普通文件复制）"""
        import os
        template_dir = self.temp_dir / "template"
        template_dir.mkdir()

        # 创建源文件
        source_file = template_dir / "source.txt"
        source_file.write_text("Original content", encoding="utf-8")

        # 创建符号链接（如果平台支持）
        symlink_file = template_dir / "link.txt"
        try:
            os.symlink(source_file, symlink_file)
            has_symlink = True
        except (OSError, NotImplementedError):
            # 平台不支持符号链接，跳过测试
            has_symlink = False

        if has_symlink:
            project_dir = self.temp_dir / "project"
            project_dir.mkdir()

            result = copy_template_files(template_dir, project_dir, self.context)

            # 验证符号链接被复制为普通文件
            copied_files = [str(p.relative_to(project_dir)) for p in result.copied]
            self.assertIn("link.txt", copied_files)

            # 验证链接内容被复制（而不是保持符号链接）
            copied_file = project_dir / "link.txt"
            self.assertFalse(copied_file.is_symlink())
            self.assertEqual(copied_file.read_text(encoding="utf-8"), "Original content")


if __name__ == "__main__":
    unittest.main()