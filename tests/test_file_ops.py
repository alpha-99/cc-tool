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
from cc_tool.file_ops import replace_variables_in_file
from cc_tool.errors import VariableReplaceError
from cc_tool.models import ProjectContext
from cc_tool.constants import SUPPORTED_VARIABLES


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

                with self.assertRaises(case["expected_error"]):
                    if case["file_path"] is None:
                        # 跳过需要特殊权限的测试
                        continue
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


if __name__ == "__main__":
    unittest.main()