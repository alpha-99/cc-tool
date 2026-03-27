""".gitignore管理模块

本模块负责管理项目的.gitignore文件。
"""

from pathlib import Path
from typing import List, Set

from .errors import GitignoreError
from .constants import GITIGNORE_RULES


def manage_gitignore(
    project_dir: Path,
    language: str,
    dry_run: bool = False
) -> bool:
    """管理项目的.gitignore文件

    Args:
        project_dir: 项目目录路径
        language: 编程语言类型

    Raises:
        GitignoreError: .gitignore操作失败
    """
    try:
        gitignore_path = project_dir / ".gitignore"

        # 构建所有规则行
        rules: List[str] = []

        # 添加通用规则
        rules.extend(GITIGNORE_RULES.get("claude_code", []))
        rules.extend(GITIGNORE_RULES.get("ide", []))
        rules.extend(GITIGNORE_RULES.get("os", []))

        # 添加语言特定规则
        language_specific = GITIGNORE_RULES.get("language_specific", {})
        if language in language_specific:
            # 添加语言特定规则标题
            # 特殊处理JavaScript的大小写
            if language == "javascript":
                language_title = "# JavaScript特定规则"
            else:
                language_title = f"# {language.capitalize()}特定规则"
            rules.append(language_title)
            rules.extend(language_specific[language])

        # 如果没有任何规则，直接返回False
        if not rules:
            return False

        # 读取现有行（如果文件存在）
        existing_lines: List[str] = []
        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding="utf-8")
            existing_lines = [line.rstrip("\n") for line in content.splitlines()]

        # 收集缺失的规则行
        missing_rules: List[str] = []
        for rule in rules:
            # 跳过空行
            if not rule.strip():
                continue
            # 检查规则是否已存在（精确匹配）
            if rule not in existing_lines:
                missing_rules.append(rule)

        # 如果没有缺失规则，直接返回False
        if not missing_rules:
            return False

        # 如果有缺失规则，但在dry-run模式下，返回True但不写入文件
        if dry_run:
            return True

        # 准备新内容
        new_lines = existing_lines.copy()
        # 如果现有内容不为空且最后一行不是空行，添加一个空行分隔
        if existing_lines and existing_lines[-1].strip() != "":
            new_lines.append("")
        new_lines.extend(missing_rules)

        # 写入文件
        gitignore_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return True

    except Exception as e:
        raise GitignoreError(f"管理.gitignore文件失败: {str(e)}")