"""用户配置测试模块

本模块包含对用户级配置初始化功能的表格驱动测试。
测试覆盖目录创建、文件创建、跳过已存在项等场景。
"""

import unittest
import tempfile
import shutil
import sys
from pathlib import Path
from unittest import mock

# 导入被测试模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from cc_tool.user_config import initialize_user_config
from cc_tool.errors import UserConfigError


class TestInitializeUserConfig(unittest.TestCase):
    """测试用户配置初始化功能"""

    def setUp(self):
        """每个测试前的准备工作"""
        self.temp_dir = Path(tempfile.mkdtemp())
        # 创建模拟的家目录
        self.mock_home = self.temp_dir / "home"
        self.mock_home.mkdir()

    def tearDown(self):
        """每个测试后的清理工作"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @mock.patch('pathlib.Path.home')
    def test_create_directory_structure(self, mock_home):
        """测试创建~/.claude/目录结构"""
        test_cases = [
            {
                "name": "创建所有目录和文件",
                "existing_items": [],
                "expected_dirs": [
                    ".claude",
                    ".claude/agents",
                    ".claude/commands",
                    ".claude/hooks",
                    ".claude/skills",
                ],
                "expected_files": [
                    ".claude/settings.json",
                    ".claude/CLAUDE.md",
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                # 设置模拟的家目录
                mock_home.return_value = self.mock_home

                # 创建已存在的项（如果有）
                for item in case["existing_items"]:
                    item_path = self.mock_home / item
                    if item.endswith('/'):
                        item_path.mkdir(parents=True, exist_ok=True)
                    else:
                        item_path.parent.mkdir(parents=True, exist_ok=True)
                        item_path.write_text("Existing content", encoding="utf-8")

                # 调用初始化函数
                initialize_user_config()

                # 验证预期目录存在
                for dir_rel in case["expected_dirs"]:
                    dir_path = self.mock_home / dir_rel
                    self.assertTrue(dir_path.exists())
                    self.assertTrue(dir_path.is_dir())

                # 验证预期文件存在
                for file_rel in case["expected_files"]:
                    file_path = self.mock_home / file_rel
                    self.assertTrue(file_path.exists())
                    self.assertTrue(file_path.is_file())

                # 验证文件内容包含基本注释模板
                settings_path = self.mock_home / ".claude/settings.json"
                settings_content = settings_path.read_text(encoding="utf-8")
                # 验证JSON包含permissions字段
                self.assertIn("permissions", settings_content)

                claude_md_path = self.mock_home / ".claude/CLAUDE.md"
                claude_md_content = claude_md_path.read_text(encoding="utf-8")
                self.assertIn("# Claude Code 用户级配置", claude_md_content)

    @mock.patch('pathlib.Path.home')
    def test_skip_existing_directories(self, mock_home):
        """测试跳过已存在的目录"""
        mock_home.return_value = self.mock_home

        # 预先创建部分目录结构
        existing_dir = self.mock_home / ".claude"
        existing_dir.mkdir()
        agents_dir = existing_dir / "agents"
        agents_dir.mkdir()

        # 在agents目录中创建一个文件，验证它不会被覆盖
        existing_file = agents_dir / "existing_agent.py"
        existing_file.write_text("Existing agent definition", encoding="utf-8")

        # 调用初始化函数
        initialize_user_config()

        # 验证预先创建的目录仍然存在
        self.assertTrue(existing_dir.exists())
        self.assertTrue(agents_dir.exists())

        # 验证现有文件未被修改
        self.assertTrue(existing_file.exists())
        self.assertEqual(
            existing_file.read_text(encoding="utf-8"),
            "Existing agent definition"
        )

        # 验证其他目录和文件被创建
        self.assertTrue((self.mock_home / ".claude/commands").exists())
        self.assertTrue((self.mock_home / ".claude/settings.json").exists())

    @mock.patch('pathlib.Path.home')
    def test_skip_existing_files(self, mock_home):
        """测试跳过已存在的文件"""
        mock_home.return_value = self.mock_home

        # 预先创建目录结构
        claude_dir = self.mock_home / ".claude"
        claude_dir.mkdir()

        # 预先创建settings.json文件
        settings_file = claude_dir / "settings.json"
        settings_content = '{"existing": "configuration"}'
        settings_file.write_text(settings_content, encoding="utf-8")

        # 调用初始化函数
        initialize_user_config()

        # 验证现有文件未被修改
        self.assertEqual(
            settings_file.read_text(encoding="utf-8"),
            settings_content
        )

        # 验证其他文件被创建
        self.assertTrue((claude_dir / "CLAUDE.md").exists())

    @mock.patch('pathlib.Path.home')
    def test_create_basic_config_files(self, mock_home):
        """测试创建基本配置文件（含注释模板）"""
        mock_home.return_value = self.mock_home

        # 调用初始化函数
        initialize_user_config()

        # 验证settings.json包含基本结构和注释
        settings_path = self.mock_home / ".claude/settings.json"
        settings_content = settings_path.read_text(encoding="utf-8")

        # 检查JSON结构
        self.assertIn('"permissions"', settings_content)
        self.assertIn('"defaultMode"', settings_content)
        self.assertIn('"allow"', settings_content)
        self.assertIn('"ask"', settings_content)
        self.assertIn('"deny"', settings_content)

        # 验证CLAUDE.md包含基本模板
        claude_md_path = self.mock_home / ".claude/CLAUDE.md"
        claude_md_content = claude_md_path.read_text(encoding="utf-8")
        self.assertIn("# Claude Code 用户级配置", claude_md_content)
        self.assertIn("## 用户级指令", claude_md_content)

    @mock.patch('pathlib.Path.home')
    def test_cross_platform_path_handling(self, mock_home):
        """测试跨平台路径处理"""
        test_cases = [
            {
                "name": "Unix风格路径",
                "home_path": Path("/home/testuser"),
            },
            {
                "name": "Windows风格路径",
                "home_path": Path("C:\\Users\\TestUser"),
            },
            {
                "name": "路径包含空格",
                "home_path": Path("/home/test user"),
            },
            {
                "name": "路径包含特殊字符",
                "home_path": Path("/home/test-user_123"),
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                # 创建模拟的家目录结构
                mock_home_dir = self.temp_dir / case["name"]
                mock_home_dir.mkdir()
                mock_home.return_value = mock_home_dir

                # 调用初始化函数
                initialize_user_config()

                # 验证.claude目录被创建
                claude_dir = mock_home_dir / ".claude"
                self.assertTrue(claude_dir.exists())

                # 验证子目录被创建
                expected_dirs = ["agents", "commands", "hooks", "skills"]
                for subdir in expected_dirs:
                    self.assertTrue((claude_dir / subdir).exists())

                # 验证配置文件被创建
                self.assertTrue((claude_dir / "settings.json").exists())
                self.assertTrue((claude_dir / "CLAUDE.md").exists())

    @mock.patch('pathlib.Path.home')
    def test_error_handling(self, mock_home):
        """测试错误处理（如权限不足）"""
        mock_home.return_value = self.mock_home

        # 创建一个只读目录模拟权限问题
        read_only_dir = self.mock_home / ".claude"
        read_only_dir.mkdir()
        read_only_dir.chmod(0o444)  # 只读权限

        try:
            # 应该抛出异常
            with self.assertRaises(UserConfigError):
                initialize_user_config()
        finally:
            # 恢复权限以便清理
            read_only_dir.chmod(0o755)


if __name__ == "__main__":
    unittest.main()