""".gitignore管理测试模块

本模块包含对.gitignore管理功能的表格驱动测试。
测试覆盖文件创建、规则追加、语言特定规则等场景。
"""

import unittest
import tempfile
import shutil
import sys
from pathlib import Path

# 导入被测试模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from cc_tool.gitignore import manage_gitignore
from cc_tool.errors import GitignoreError


class TestManageGitignore(unittest.TestCase):
    """测试.gitignore管理功能"""

    def setUp(self):
        """每个测试前的准备工作"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """每个测试后的清理工作"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_gitignore_file(self):
        """测试创建.gitignore文件（当文件不存在时）"""
        test_cases = [
            {
                "name": "创建基础.gitignore文件",
                "language": "python",
                "expected_rules": [
                    "# Claude Code 本地配置",
                    ".claude/settings.local.json",
                    "# IDE 配置目录",
                    ".vscode/",
                    ".idea/",
                    "# 操作系统文件",
                    "*.DS_Store",
                    "# Python特定规则",
                    "__pycache__/",
                    "*.pyc",
                ],
            },
            {
                "name": "JavaScript语言特定规则",
                "language": "javascript",
                "expected_rules": [
                    "# Claude Code 本地配置",
                    ".claude/settings.local.json",
                    "# IDE 配置目录",
                    ".vscode/",
                    ".idea/",
                    "# 操作系统文件",
                    "*.DS_Store",
                    "# JavaScript特定规则",
                    "node_modules/",
                ],
            },
            {
                "name": "Go语言特定规则",
                "language": "go",
                "expected_rules": [
                    "# Claude Code 本地配置",
                    ".claude/settings.local.json",
                    "# IDE 配置目录",
                    ".vscode/",
                    ".idea/",
                    "# 操作系统文件",
                    "*.DS_Store",
                    "# Go特定规则",
                    "dist/",
                    "build/",
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                project_dir = self.temp_dir / case["name"]
                project_dir.mkdir()

                # 调用管理函数
                manage_gitignore(project_dir, case["language"])

                # 验证.gitignore文件存在
                gitignore_path = project_dir / ".gitignore"
                self.assertTrue(gitignore_path.exists())

                # 验证文件内容包含预期规则
                content = gitignore_path.read_text(encoding="utf-8")
                lines = [line.rstrip() for line in content.splitlines() if line.strip()]

                # 检查每条预期规则是否存在
                for expected_rule in case["expected_rules"]:
                    self.assertIn(expected_rule, lines)

    def test_append_missing_rules(self):
        """测试追加缺失规则到已存在的.gitignore文件"""
        test_cases = [
            {
                "name": "追加缺失的Claude Code规则",
                "initial_content": "# 现有规则\n*.log\n",
                "language": "python",
                "expected_additional_rules": [
                    "# Claude Code 本地配置",
                    ".claude/settings.local.json",
                ],
            },
            {
                "name": "追加缺失的语言特定规则",
                "initial_content": "# Claude Code 本地配置\n.claude/settings.local.json\n",
                "language": "javascript",
                "expected_additional_rules": [
                    "# JavaScript特定规则",
                    "node_modules/",
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                project_dir = self.temp_dir / case["name"]
                project_dir.mkdir()

                # 创建初始.gitignore文件
                gitignore_path = project_dir / ".gitignore"
                gitignore_path.write_text(case["initial_content"], encoding="utf-8")

                # 调用管理函数
                manage_gitignore(project_dir, case["language"])

                # 验证文件内容包含初始内容和新增规则
                content = gitignore_path.read_text(encoding="utf-8")
                lines = [line.rstrip() for line in content.splitlines()]

                # 验证初始内容仍然存在
                initial_lines = [line.rstrip() for line in case["initial_content"].splitlines() if line.strip()]
                for initial_line in initial_lines:
                    self.assertIn(initial_line, lines)

                # 验证新增规则存在
                for expected_rule in case["expected_additional_rules"]:
                    self.assertIn(expected_rule, lines)

    def test_no_duplicate_rules(self):
        """测试不添加重复规则"""
        test_cases = [
            {
                "name": "规则已存在时不重复添加",
                "initial_content": "# Claude Code 本地配置\n.claude/settings.local.json\n",
                "language": "python",
                "expected_rule_count": 11,  # 初始2行 + ide规则3行 + os规则2行 + python特定规则3行 + 空行分隔1行
            },
            {
                "name": "部分规则已存在",
                "initial_content": "# Claude Code 本地配置\n.claude/settings.local.json\n*.DS_Store\n",
                "language": "python",
                # 应该只添加缺失的规则
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                project_dir = self.temp_dir / case["name"]
                project_dir.mkdir()

                # 创建初始.gitignore文件
                gitignore_path = project_dir / ".gitignore"
                gitignore_path.write_text(case["initial_content"], encoding="utf-8")

                # 记录初始行数
                initial_lines = gitignore_path.read_text(encoding="utf-8").splitlines()

                # 调用管理函数
                manage_gitignore(project_dir, case["language"])

                # 验证没有重复行
                final_content = gitignore_path.read_text(encoding="utf-8")
                final_lines = final_content.splitlines()

                # 如果规则已存在，行数不应增加
                if "expected_rule_count" in case:
                    self.assertEqual(len(final_lines), case["expected_rule_count"])

                # 验证没有完全重复的行（忽略空行）
                seen = set()
                duplicates = []
                for line in final_lines:
                    if line.strip() and line in seen:
                        duplicates.append(line)
                    seen.add(line)
                self.assertEqual(len(duplicates), 0, f"发现重复行: {duplicates}")

    def test_language_specific_rules(self):
        """测试不同语言的特定规则"""
        test_cases = [
            {
                "name": "Python规则",
                "language": "python",
                "expected_rules": ["__pycache__/", "*.pyc"],
                "unexpected_rules": ["node_modules/", "target/"],
            },
            {
                "name": "JavaScript规则",
                "language": "javascript",
                "expected_rules": ["node_modules/"],
                "unexpected_rules": ["__pycache__/", "*.pyc", "target/"],
            },
            {
                "name": "Rust规则",
                "language": "rust",
                "expected_rules": ["target/"],
                "unexpected_rules": ["__pycache__/", "node_modules/"],
            },
            {
                "name": "Java规则",
                "language": "java",
                "expected_rules": ["target/", "build/"],
                "unexpected_rules": ["__pycache__/", "node_modules/"],
            },
            {
                "name": "Go规则",
                "language": "go",
                "expected_rules": ["dist/", "build/"],
                "unexpected_rules": ["__pycache__/", "node_modules/", "target/"],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                project_dir = self.temp_dir / case["name"]
                project_dir.mkdir()

                # 调用管理函数
                manage_gitignore(project_dir, case["language"])

                # 验证.gitignore文件存在
                gitignore_path = project_dir / ".gitignore"
                self.assertTrue(gitignore_path.exists())

                # 验证包含语言特定规则
                content = gitignore_path.read_text(encoding="utf-8")
                for expected_rule in case["expected_rules"]:
                    self.assertIn(expected_rule, content)

                # 验证不包含其他语言规则
                for unexpected_rule in case["unexpected_rules"]:
                    self.assertNotIn(unexpected_rule, content)

    def test_missing_rules_in_existing_file(self):
        """测试文件已存在但规则缺失的情况"""
        project_dir = self.temp_dir / "test"
        project_dir.mkdir()

        # 创建只有注释的.gitignore文件
        gitignore_path = project_dir / ".gitignore"
        gitignore_path.write_text("# 这是一个测试文件\n", encoding="utf-8")

        # 调用管理函数
        manage_gitignore(project_dir, "python")

        # 验证缺失的规则被添加
        content = gitignore_path.read_text(encoding="utf-8")
        self.assertIn("# Claude Code 本地配置", content)
        self.assertIn(".claude/settings.local.json", content)
        self.assertIn("# Python特定规则", content)
        self.assertIn("__pycache__/", content)

        # 验证原始注释仍然存在
        self.assertIn("# 这是一个测试文件", content)


if __name__ == "__main__":
    unittest.main()