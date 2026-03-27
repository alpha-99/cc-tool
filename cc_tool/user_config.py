"""用户配置模块

本模块负责初始化用户级Claude Code配置框架。
"""

import json
from pathlib import Path
from typing import List
from .errors import UserConfigError


def initialize_user_config() -> List[Path]:
    """初始化用户级Claude Code配置框架

    Returns:
        list[Path]: 创建的文件路径列表

    Raises:
        UserConfigError: 用户配置初始化失败
    """
    try:
        home_dir = Path.home()
        claude_dir = home_dir / ".claude"
        created_files = []

        # 创建.claude目录及其子目录
        directories = [
            claude_dir,
            claude_dir / "agents",
            claude_dir / "commands",
            claude_dir / "hooks",
            claude_dir / "skills",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        # 创建settings.json（如果不存在）
        settings_path = claude_dir / "settings.json"
        if not settings_path.exists():
            settings_content = {
                "permissions": {
                    "defaultMode": "plan",
                    "allow": [
                        "Read(*.py)",
                        "Read(pyproject.toml)",
                        "Read(requirements.txt)",
                        "Read(setup.py)",
                        "Read(README.md)",
                        "Grep",
                        "Glob",
                        "LS",
                    ],
                    "ask": [
                        "Write",
                        "Edit",
                        "MultiEdit",
                        "Bash(pip:install:*)",
                        "Bash(git:add:*)",
                    ],
                    "deny": [
                        "Read(./.env*)",
                        "Read(*.pem)",
                        "Read(*.key)",
                        "Bash(rm:*)",
                        "Bash(git:push:*)",
                    ]
                }
            }
            settings_path.write_text(
                json.dumps(settings_content, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            created_files.append(settings_path)

        # 创建CLAUDE.md（如果不存在）
        claude_md_path = claude_dir / "CLAUDE.md"
        if not claude_md_path.exists():
            claude_md_content = """# Claude Code 用户级配置

## 用户级指令

在此文件中定义适用于所有项目的Claude Code指令。

## 配置说明

- `agents/`: 自定义Agent定义
- `commands/`: 自定义命令定义
- `hooks/`: 自定义钩子定义
- `skills/`: 自定义技能定义
- `settings.json`: 权限配置

## 使用提示

1. 将项目特定的配置放在项目目录的`.claude/`目录中
2. 用户级配置会作为默认配置，可被项目级配置覆盖
"""
            claude_md_path.write_text(claude_md_content, encoding="utf-8")
            created_files.append(claude_md_path)

        return created_files

    except Exception as e:
        raise UserConfigError(f"初始化用户配置失败: {str(e)}")