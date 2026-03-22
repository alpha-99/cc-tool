"""错误类型测试模块

本模块测试cc-tool项目中定义的所有自定义异常类。
"""

import unittest
import sys
from pathlib import Path

# 导入被测试模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from cc_tool.errors import (
    CCToolError,
    ProjectDirectoryError,
    LanguageNotSupportedError,
    TemplateNotFoundError,
    FileOperationError,
    VariableReplaceError,
    GitignoreError,
    UserConfigError,
)


class TestErrorClasses(unittest.TestCase):
    """测试自定义异常类的继承关系和基本行为"""

    # 表格驱动测试：异常类继承关系
    def test_exception_inheritance(self):
        """测试所有自定义异常都继承自CCToolError"""
        test_cases = [
            {
                "name": "ProjectDirectoryError",
                "exception_class": ProjectDirectoryError,
                "expected_parent": CCToolError,
            },
            {
                "name": "LanguageNotSupportedError",
                "exception_class": LanguageNotSupportedError,
                "expected_parent": CCToolError,
            },
            {
                "name": "TemplateNotFoundError",
                "exception_class": TemplateNotFoundError,
                "expected_parent": CCToolError,
            },
            {
                "name": "FileOperationError",
                "exception_class": FileOperationError,
                "expected_parent": CCToolError,
            },
            {
                "name": "VariableReplaceError",
                "exception_class": VariableReplaceError,
                "expected_parent": CCToolError,
            },
            {
                "name": "GitignoreError",
                "exception_class": GitignoreError,
                "expected_parent": CCToolError,
            },
            {
                "name": "UserConfigError",
                "exception_class": UserConfigError,
                "expected_parent": CCToolError,
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                self.assertTrue(issubclass(case["exception_class"], case["expected_parent"]))
                # 同时检查是否是Exception的子类
                self.assertTrue(issubclass(case["exception_class"], Exception))

    # 表格驱动测试：异常实例化与消息
    def test_exception_instantiation(self):
        """测试异常类的实例化和消息传递"""
        test_cases = [
            {
                "name": "带消息的ProjectDirectoryError",
                "exception_class": ProjectDirectoryError,
                "message": "项目目录不存在: /path/to/dir",
                "expected_message": "项目目录不存在: /path/to/dir",
            },
            {
                "name": "带消息的LanguageNotSupportedError",
                "exception_class": LanguageNotSupportedError,
                "message": "不支持的语言: ruby",
                "expected_message": "不支持的语言: ruby",
            },
            {
                "name": "带消息的TemplateNotFoundError",
                "exception_class": TemplateNotFoundError,
                "message": "找不到模板: python",
                "expected_message": "找不到模板: python",
            },
            {
                "name": "带消息的FileOperationError",
                "exception_class": FileOperationError,
                "message": "文件复制失败: src.txt",
                "expected_message": "文件复制失败: src.txt",
            },
            {
                "name": "带消息的VariableReplaceError",
                "exception_class": VariableReplaceError,
                "message": "变量替换失败: {{PROJECT_NAME}}",
                "expected_message": "变量替换失败: {{PROJECT_NAME}}",
            },
            {
                "name": "带消息的GitignoreError",
                "exception_class": GitignoreError,
                "message": ".gitignore文件创建失败",
                "expected_message": ".gitignore文件创建失败",
            },
            {
                "name": "带消息的UserConfigError",
                "exception_class": UserConfigError,
                "message": "用户配置初始化失败",
                "expected_message": "用户配置初始化失败",
            },
            {
                "name": "空消息的异常",
                "exception_class": CCToolError,
                "message": "",
                "expected_message": "",
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                exc = case["exception_class"](case["message"])
                self.assertEqual(str(exc), case["expected_message"])
                self.assertIsInstance(exc, CCToolError)
                self.assertIsInstance(exc, Exception)

    # 测试异常抛出和捕获
    def test_exception_raise_and_catch(self):
        """测试异常的抛出和捕获行为"""
        test_cases = [
            {
                "name": "抛出并捕获ProjectDirectoryError",
                "exception_class": ProjectDirectoryError,
                "message": "测试错误",
            },
            {
                "name": "抛出并捕获LanguageNotSupportedError",
                "exception_class": LanguageNotSupportedError,
                "message": "测试错误",
            },
            {
                "name": "抛出并捕获TemplateNotFoundError",
                "exception_class": TemplateNotFoundError,
                "message": "测试错误",
            },
            {
                "name": "抛出并捕获FileOperationError",
                "exception_class": FileOperationError,
                "message": "测试错误",
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                with self.assertRaises(case["exception_class"]) as cm:
                    raise case["exception_class"](case["message"])
                self.assertEqual(str(cm.exception), case["message"])

    # 测试异常链
    def test_exception_chaining(self):
        """测试异常链（cause和context）"""
        try:
            try:
                raise ValueError("内部错误")
            except ValueError as inner:
                raise ProjectDirectoryError("项目目录错误") from inner
        except ProjectDirectoryError as outer:
            self.assertIsInstance(outer.__cause__, ValueError)
            self.assertEqual(str(outer.__cause__), "内部错误")

    # 测试异常类本身的属性
    def test_exception_class_attributes(self):
        """测试异常类本身的属性（如docstring）"""
        self.assertIsNotNone(CCToolError.__doc__, "CCToolError应该有文档字符串")
        self.assertIsNotNone(ProjectDirectoryError.__doc__, "ProjectDirectoryError应该有文档字符串")
        self.assertIsNotNone(LanguageNotSupportedError.__doc__, "LanguageNotSupportedError应该有文档字符串")
        # 检查其他异常类的文档字符串


if __name__ == "__main__":
    unittest.main()