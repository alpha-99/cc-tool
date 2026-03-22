"""项目常量定义

本模块定义了cc-tool项目中使用的所有常量。
这些常量用于配置支持的语言、模板要求和.gitignore规则。
"""

# 支持的语言及其别名映射
# 键：标准语言名称，值：别名列表（不区分大小写）
SUPPORTED_LANGUAGES = {
    "python": ["py", "python3"],
    "javascript": ["js", "node", "typescript", "ts"],
    "go": ["golang"],
    "rust": ["rs"],
    "java": ["java"],
}

# 模板必须包含的文件列表
# 每个语言模板目录必须包含这些文件
REQUIRED_TEMPLATE_FILES = [
    ".claude/settings.json",
    "CLAUDE.md",
]

# .gitignore规则分类
# 用于组织和管理.gitignore文件内容
GITIGNORE_RULES = {
    "claude_code": [
        "# Claude Code 本地配置",
        ".claude/settings.local.json",
    ],
    "ide": [
        "# IDE 配置目录",
        ".vscode/",
        ".idea/",
    ],
    "os": [
        "# 操作系统文件",
        "*.DS_Store",
    ],
    "language_specific": {
        "python": ["__pycache__/", "*.pyc"],
        "javascript": ["node_modules/"],
        "rust": ["target/"],
        "java": ["target/", "build/"],
        "go": ["dist/", "build/"],
    },
}

# 变量占位符格式
# 模板文件中使用的变量占位符格式为 {{VARIABLE_NAME}}
VARIABLE_PATTERN = r"{{([A-Z_]+)}}"

# 支持的变量类型
SUPPORTED_VARIABLES = ["PROJECT_NAME", "PROJECT_DIR", "LANGUAGE"]

# 日志输出前缀
LOG_PREFIXES = {
    "INFO": "[INFO]",
    "WARNING": "[WARNING]",
    "ERROR": "[ERROR]",
    "DEBUG": "[DEBUG]",
}

# 版本信息
VERSION = "0.1.0"
AUTHOR = "cc-tool Development Team"
DESCRIPTION = "Claude Code 配置文件初始化工具"