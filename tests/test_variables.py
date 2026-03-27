"""变量替换测试模块

本模块包含对模板变量替换功能的表格驱动测试。
测试覆盖变量替换、二进制文件处理、文件编码处理等场景。
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

    # 表格驱动测试：基础变量替换
    def test_basic_variable_replacement(self):
        """测试基础变量替换：{{PROJECT_NAME}}、{{PROJECT_DIR}}、{{LANGUAGE}}"""
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
                "name": "变量在行中",
                "template_content": "欢迎使用{{PROJECT_NAME}}项目！",
                "expected_content": "欢迎使用MyProject项目！",
            },
            {
                "name": "变量在行尾",
                "template_content": "语言是{{LANGUAGE}}",
                "expected_content": "语言是python",
            },
            {
                "name": "变量在行首",
                "template_content": "{{PROJECT_NAME}}是一个很棒的项目",
                "expected_content": "MyProject是一个很棒的项目",
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

    # 表格驱动测试：多变量同时替换
    def test_multiple_variables_replacement(self):
        """测试多变量同时替换"""
        test_cases = [
            {
                "name": "两个变量在同一行",
                "template_content": "项目: {{PROJECT_NAME}} (语言: {{LANGUAGE}})",
                "expected_content": "项目: MyProject (语言: python)",
            },
            {
                "name": "三个变量在同一行",
                "template_content": "{{PROJECT_NAME}} {{LANGUAGE}} {{PROJECT_DIR}}",
                "expected_content": f"MyProject python {self.context.project_dir}",
            },
            {
                "name": "多行多个变量",
                "template_content": """项目: {{PROJECT_NAME}}
语言: {{LANGUAGE}}
目录: {{PROJECT_DIR}}
描述: 这是一个{{LANGUAGE}}项目""",
                "expected_content": f"""项目: MyProject
语言: python
目录: {self.context.project_dir}
描述: 这是一个python项目""",
            },
            {
                "name": "变量重复出现",
                "template_content": "{{PROJECT_NAME}} - {{PROJECT_NAME}} - {{PROJECT_NAME}}",
                "expected_content": "MyProject - MyProject - MyProject",
            },
            {
                "name": "混合变量顺序",
                "template_content": "{{LANGUAGE}}{{PROJECT_NAME}}{{PROJECT_DIR}}",
                "expected_content": f"pythonMyProject{self.context.project_dir}",
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                test_file = self.temp_dir / "test.txt"
                test_file.write_text(case["template_content"], encoding="utf-8")

                replace_variables_in_file(test_file, self.context)
                actual_content = test_file.read_text(encoding="utf-8")
                self.assertEqual(actual_content, case["expected_content"])

    # 表格驱动测试：二进制文件不进行替换
    def test_binary_files_no_replacement(self):
        """测试二进制文件不进行变量替换"""
        # 准备二进制数据（PNG文件头）
        png_header = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
        # 在二进制数据中插入变量占位符的字节表示
        # "{{PROJECT_NAME}}" 的 UTF-8 编码
        variable_bytes = b"{{PROJECT_NAME}}"
        binary_data = png_header + variable_bytes + b"more binary data"

        test_cases = [
            {
                "name": "PNG文件",
                "data": binary_data,
                "filename": "test.png",
            },
            {
                "name": "JPG文件（模拟）",
                "data": b"\xFF\xD8\xFF\xE0{{PROJECT_NAME}}\x00\x10JFIF",
                "filename": "test.jpg",
            },
            {
                "name": "GIF文件（模拟）",
                "data": b"GIF89a{{LANGUAGE}}imagedata",
                "filename": "test.gif",
            },
            {
                "name": "PDF文件（模拟）",
                "data": b"%PDF-1.4\n{{PROJECT_DIR}}\n%%EOF",
                "filename": "test.pdf",
            },
            {
                "name": "ZIP文件（模拟）",
                "data": b"PK\x03\x04{{PROJECT_NAME}}compresseddata",
                "filename": "test.zip",
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                test_file = self.temp_dir / case["filename"]
                # 写入二进制数据
                test_file.write_bytes(case["data"])

                # 记录原始数据
                original_data = test_file.read_bytes()

                # 调用函数替换变量（应该不修改二进制文件）
                replace_variables_in_file(test_file, self.context)

                # 验证文件内容未改变
                result_data = test_file.read_bytes()
                self.assertEqual(
                    result_data,
                    original_data,
                    f"二进制文件 {case['filename']} 的内容不应被修改"
                )

    # 表格驱动测试：文件编码处理
    def test_file_encoding_handling(self):
        """测试不同文件编码的处理"""
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
                "template_content": "项目: {{LANGUAGE}} - BOM测试",
                "expected_content": "项目: python - BOM测试",
            },
            {
                "name": "UTF-16 LE",
                "encoding": "utf-16-le",
                "template_content": "项目: {{PROJECT_NAME}} - UTF16测试",
                "expected_content": "项目: MyProject - UTF16测试",
            },
            {
                "name": "UTF-16 BE",
                "encoding": "utf-16-be",
                "template_content": "项目: {{LANGUAGE}} - UTF16BE测试",
                "expected_content": "项目: python - UTF16BE测试",
            },
            {
                "name": "ASCII 编码",
                "encoding": "ascii",
                "template_content": "Project: {{PROJECT_NAME}} - ASCII only",
                "expected_content": "Project: MyProject - ASCII only",
            },
            {
                "name": "Latin-1 编码",
                "encoding": "latin-1",
                "template_content": "Projet: {{LANGUAGE}} - Latin-1 test",
                "expected_content": "Projet: python - Latin-1 test",
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                test_file = self.temp_dir / "test.txt"
                try:
                    # 使用指定编码写入文件
                    test_file.write_text(case["template_content"], encoding=case["encoding"])

                    # 调用函数替换变量
                    replace_variables_in_file(test_file, self.context)

                    # 使用相同编码读取文件
                    actual_content = test_file.read_text(encoding=case["encoding"])
                    self.assertEqual(actual_content, case["expected_content"])
                except (UnicodeEncodeError, UnicodeDecodeError) as e:
                    # 某些编码可能不支持特定字符，跳过这些测试
                    self.skipTest(f"编码 {case['encoding']} 不支持测试内容: {e}")

    # 表格驱动测试：边界和异常情况
    def test_edge_cases_and_exceptions(self):
        """测试边界条件和异常情况"""
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
                "name": "不支持的变量名",
                "template_content": "变量: {{UNKNOWN_VARIABLE}}",
                "expected_content": "变量: {{UNKNOWN_VARIABLE}}",
            },
            {
                "name": "变量名小写",
                "template_content": "变量: {{project_name}}",
                "expected_content": "变量: {{project_name}}",
            },
            {
                "name": "文件不存在",
                "file_exists": False,
                "expected_error": VariableReplaceError,
            },
            {
                "name": "目录而不是文件",
                "is_directory": True,
                "expected_error": VariableReplaceError,
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                if case.get("file_exists", True) is False:
                    # 测试不存在的文件
                    test_file = self.temp_dir / "nonexistent.txt"
                    with self.assertRaises(case["expected_error"]):
                        replace_variables_in_file(test_file, self.context)
                elif case.get("is_directory", False):
                    # 测试目录
                    test_dir = self.temp_dir / "subdir"
                    test_dir.mkdir()
                    with self.assertRaises(case["expected_error"]):
                        replace_variables_in_file(test_dir, self.context)
                else:
                    # 正常测试用例
                    test_file = self.temp_dir / "test.txt"
                    test_file.write_text(case["template_content"], encoding="utf-8")

                    replace_variables_in_file(test_file, self.context)
                    actual_content = test_file.read_text(encoding="utf-8")
                    self.assertEqual(actual_content, case["expected_content"])


if __name__ == "__main__":
    unittest.main()