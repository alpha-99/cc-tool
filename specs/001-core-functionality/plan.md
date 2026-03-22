# cc-tool 技术实现方案
## 版本: 1.0.0
## 最后更新: 2026-03-21

---

## 1. 技术上下文总结

### 1.1 技术选型
- **编程语言**: Python 3.11+
- **依赖策略**: 严格遵循"简单性原则"，仅使用Python标准库，不引入外部框架或第三方依赖
- **构建系统**: 使用Python内置的`setuptools`进行打包，通过`pyproject.toml`配置
- **任务运行器**: 使用标准库`argparse`进行命令行解析，不依赖外部任务运行器
- **测试框架**: 使用标准库`unittest`，或根据团队偏好使用`pytest`（但需明确理由）

### 1.2 核心约束
1. **跨平台兼容**: 支持Linux、macOS和Windows（通过WSL或原生）
2. **性能要求**: 初始化包含10个文件的模板应在2秒内完成
3. **资源效率**: 递归复制时避免深度嵌套导致的性能问题
4. **最小化依赖**: 优先使用标准库，外部依赖需明确理由

### 1.3 开发环境
- Python 3.11+ 虚拟环境
- 版本控制: Git，遵循Conventional Commits规范
- 代码质量: 使用标准库工具进行代码检查（如`mypy`可选，但非必须）

---

## 2. "合宪性"审查

### 2.1 第一条：简单性原则 (Simplicity First)
| 宪法条款 | 本方案符合性 | 具体实现 |
|----------|--------------|----------|
| **1.1 (YAGNI)** | ✅ 完全符合 | 仅实现`spec.md`中明确要求的功能，不添加额外功能 |
| **1.2 (标准库优先)** | ✅ 完全符合 | 仅使用Python标准库，不引入外部依赖 |
| **1.3 (反过度工程)** | ✅ 完全符合 | 使用简单的函数和数据结构，避免不必要的抽象 |

### 2.2 第二条：测试先行铁律 (Test-First Imperative)
| 宪法条款 | 本方案符合性 | 具体实现 |
|----------|--------------|----------|
| **2.1 (TDD循环)** | ✅ 完全符合 | 所有新功能严格遵循"Red-Green-Refactor"循环 |
| **2.2 (表格驱动)** | ✅ 完全符合 | 单元测试优先采用表格驱动测试风格 |
| **2.3 (拒绝Mocks)** | ✅ 完全符合 | 优先编写集成测试，使用真实的文件系统操作 |

### 2.3 第三条：明确性原则 (Clarity and Explicitness)
| 宪法条款 | 本方案符合性 | 具体实现 |
|----------|--------------|----------|
| **3.1 (错误处理)** | ✅ 完全符合 | 所有错误显式捕获，提供清晰的错误信息，避免静默崩溃 |
| **3.2 (无全局变量)** | ✅ 完全符合 | 所有依赖通过函数参数或对象成员显式注入 |
| **3.3 (模块化与命名空间)** | ✅ 完全符合 | 使用Python模块系统组织代码，包结构清晰 |
| **3.4 ("Pythonic"代码)** | ✅ 完全符合 | 使用Python风格的代码（迭代器、上下文管理器等） |

---

## 3. 项目结构细化

### 3.1 目录结构
```
cc-tool/
├── cc_tool/                    # 主包
│   ├── __init__.py            # 包初始化
│   ├── cli.py                 # 命令行接口
│   ├── core.py                # 核心业务逻辑
│   ├── template.py            # 模板管理
│   ├── file_ops.py            # 文件操作
│   ├── variables.py           # 变量替换
│   ├── gitignore.py           # .gitignore管理
│   ├── user_config.py         # 用户级配置
│   ├── logger.py              # 日志系统
│   └── errors.py              # 错误定义
├── templates/                 # 内置模板（MVP阶段）
│   ├── python/               # Python语言模板
│   │   ├── .claude/
│   │   │   ├── settings.json
│   │   │   ├── agents/       # （空目录）
│   │   │   ├── commands/     # （空目录）
│   │   │   ├── hooks/        # （空目录）
│   │   │   └── skills/       # （空目录）
│   │   ├── CLAUDE.md
│   │   ├── constitution.md   # （可选）
│   │   └── specs/            # （空目录）
│   ├── javascript/           # JavaScript语言模板
│   ├── go/                   # Go语言模板
│   ├── rust/                 # Rust语言模板
│   └── java/                 # Java语言模板
├── tests/                    # 测试代码
│   ├── __init__.py
│   ├── test_cli.py          # 命令行测试
│   ├── test_core.py         # 核心逻辑测试
│   ├── test_template.py     # 模板测试
│   ├── test_file_ops.py     # 文件操作测试
│   ├── test_variables.py    # 变量替换测试
│   ├── test_gitignore.py    # .gitignore测试
│   ├── test_user_config.py  # 用户配置测试
│   └── integration/         # 集成测试
│       └── test_end_to_end.py
├── specs/                    # 需求规范
│   └── 001-core-functionality/
│       ├── spec.md          # 需求规格
│       └── plan.md          # 本技术方案
├── .claude/                 # 项目自身配置
│   └── settings.json
├── CLAUDE.md                # 项目指令
├── constitution.md          # 项目宪法
├── pyproject.toml           # 项目配置
├── README.md                # 项目说明
└── .gitignore              # Git忽略规则
```

### 3.2 包职责与依赖关系

#### 3.2.1 核心包 (`cc_tool/`)
- **`cli.py`**: 命令行参数解析，依赖`core.py`
- **`core.py`**: 协调所有模块，实现主业务流程
- **`template.py`**: 模板查找、验证，不依赖其他模块
- **`file_ops.py`**: 文件复制、目录创建，依赖`variables.py`进行变量替换
- **`variables.py`**: 模板变量替换逻辑，独立模块
- **`gitignore.py`**: .gitignore文件管理，独立模块
- **`user_config.py`**: 用户级配置初始化，独立模块
- **`logger.py`**: 日志输出，被所有模块使用
- **`errors.py`**: 自定义异常定义，被所有模块使用

#### 3.2.2 依赖关系图
```
cli.py → core.py → {template.py, file_ops.py, gitignore.py, user_config.py}
file_ops.py → variables.py
所有模块 → logger.py
所有模块 → errors.py
```

#### 3.2.3 模块内聚原则
- 每个模块专注于单一职责
- 模块间通过清晰定义的接口通信
- 避免循环依赖

---

## 4. 核心数据结构

### 4.1 数据类定义

```python
# 在 cc_tool/models.py 中定义
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class TemplateConfig:
    """模板配置信息"""
    language: str                    # 语言类型（如 'python'）
    alias: List[str]                 # 语言别名（如 ['py', 'python3']）
    template_dir: Path               # 模板目录路径
    required_files: List[str]        # 必须包含的文件列表

@dataclass
class ProjectContext:
    """项目上下文信息"""
    project_dir: Path               # 项目目录路径
    project_name: str               # 项目名称（从目录名提取）
    language: str                   # 编程语言类型
    verbose: bool                   # 详细模式标志
    dry_run: bool                   # 预览模式标志
    quiet: bool                     # 静默模式标志

@dataclass
class CopyResult:
    """文件复制结果"""
    copied: List[Path]              # 成功复制的文件
    skipped: List[Path]             # 跳过的文件（已存在）
    errors: List[Tuple[Path, str]]  # 错误列表（文件路径，错误信息）

@dataclass
class GitignoreRule:
    """Gitignore规则定义"""
    category: str                   # 规则类别（如 'Claude Code', 'IDE', 'OS'）
    rules: List[str]                # 规则内容列表
```

### 4.2 常量定义

```python
# 在 cc_tool/constants.py 中定义
SUPPORTED_LANGUAGES = {
    'python': ['py', 'python3'],
    'javascript': ['js', 'node', 'typescript', 'ts'],
    'go': ['golang'],
    'rust': ['rs'],
    'java': ['java']
}

# 模板必须包含的文件
REQUIRED_TEMPLATE_FILES = [
    '.claude/settings.json',
    'CLAUDE.md'
]

# Gitignore规则分类
GITIGNORE_RULES = {
    'claude_code': [
        '# Claude Code 本地配置',
        '.claude/settings.local.json'
    ],
    'ide': [
        '# IDE 配置目录',
        '.vscode/',
        '.idea/'
    ],
    'os': [
        '# 操作系统文件',
        '*.DS_Store'
    ],
    'language_specific': {
        'python': ['__pycache__/', '*.pyc'],
        'javascript': ['node_modules/'],
        'rust': ['target/'],
        'java': ['target/', 'build/'],
        'go': ['dist/', 'build/']
    }
}
```

---

## 5. 接口设计

### 5.1 命令行接口 (CLI)

#### 5.1.1 命令格式
```
cc-tool [OPTIONS] PROJECT_DIR LANGUAGE
```

#### 5.1.2 参数说明
- **`PROJECT_DIR`**: 项目目录路径（必需）
- **`LANGUAGE`**: 编程语言类型（必需），不区分大小写，支持别名

#### 5.1.3 选项说明
| 选项 | 短选项 | 描述 |
|------|--------|------|
| `--help` | `-h` | 显示帮助信息 |
| `--version` | `-v` | 显示版本信息 |
| `--list-languages` | `-l` | 列出所有支持的语言类型 |
| `--list-templates` | `-t` | 列出所有可用的模板 |
| `--dry-run` | `-n` | 预览模式，显示将要执行的操作但不实际执行 |
| `--verbose` | `-V` | 详细模式，输出调试信息 |
| `--quiet` | `-q` | 静默模式，只输出错误信息 |

### 5.2 程序化API

#### 5.2.1 核心API函数

```python
# cc_tool/core.py
def initialize_project(
    project_dir: Union[str, Path],
    language: str,
    verbose: bool = False,
    dry_run: bool = False,
    quiet: bool = False
) -> CopyResult:
    """初始化项目配置

    Args:
        project_dir: 项目目录路径
        language: 编程语言类型
        verbose: 详细模式
        dry_run: 预览模式
        quiet: 静默模式

    Returns:
        CopyResult: 复制结果统计

    Raises:
        ProjectDirectoryError: 项目目录错误
        LanguageNotSupportedError: 语言不支持
        TemplateNotFoundError: 模板不存在
        PermissionError: 权限不足
    """
    pass

# cc_tool/template.py
def find_template(language: str) -> TemplateConfig:
    """查找指定语言的模板

    Args:
        language: 编程语言类型

    Returns:
        TemplateConfig: 模板配置信息

    Raises:
        LanguageNotSupportedError: 语言不支持
        TemplateNotFoundError: 模板不存在
    """
    pass

def validate_template(template_dir: Path) -> bool:
    """验证模板目录完整性

    Args:
        template_dir: 模板目录路径

    Returns:
        bool: 模板是否有效

    Raises:
        TemplateValidationError: 模板验证失败
    """
    pass

# cc_tool/file_ops.py
def copy_template_files(
    template_dir: Path,
    project_dir: Path,
    context: ProjectContext,
    dry_run: bool = False
) -> CopyResult:
    """复制模板文件到项目目录

    Args:
        template_dir: 模板目录路径
        project_dir: 项目目录路径
        context: 项目上下文信息
        dry_run: 预览模式

    Returns:
        CopyResult: 复制结果统计
    """
    pass

def replace_variables_in_file(
    file_path: Path,
    context: ProjectContext
) -> None:
    """替换文件中的模板变量

    Args:
        file_path: 文件路径
        context: 项目上下文信息

    Raises:
        VariableReplaceError: 变量替换失败
    """
    pass

# cc_tool/gitignore.py
def manage_gitignore(
    project_dir: Path,
    language: str
) -> None:
    """管理项目的.gitignore文件

    Args:
        project_dir: 项目目录路径
        language: 编程语言类型

    Raises:
        GitignoreError: .gitignore操作失败
    """
    pass

# cc_tool/user_config.py
def initialize_user_config() -> None:
    """初始化用户级Claude Code配置框架

    Raises:
        UserConfigError: 用户配置初始化失败
    """
    pass
```

#### 5.2.2 错误处理API

```python
# cc_tool/errors.py
class CCToolError(Exception):
    """所有cc-tool异常的基类"""
    pass

class ProjectDirectoryError(CCToolError):
    """项目目录相关错误"""
    pass

class LanguageNotSupportedError(CCToolError):
    """语言不支持错误"""
    pass

class TemplateNotFoundError(CCToolError):
    """模板不存在错误"""
    pass

class FileOperationError(CCToolError):
    """文件操作错误"""
    pass

class VariableReplaceError(CCToolError):
    """变量替换错误"""
    pass

class GitignoreError(CCToolError):
    """.gitignore操作错误"""
    pass

class UserConfigError(CCToolError):
    """用户配置错误"""
    pass
```

### 5.3 日志接口

```python
# cc_tool/logger.py
def setup_logger(verbose: bool = False, quiet: bool = False) -> logging.Logger:
    """配置日志记录器

    Args:
        verbose: 详细模式
        quiet: 静默模式

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    pass

def log_info(message: str) -> None:
    """记录信息日志"""
    pass

def log_warning(message: str) -> None:
    """记录警告日志"""
    pass

def log_error(message: str) -> None:
    """记录错误日志"""
    pass

def log_debug(message: str) -> None:
    """记录调试日志"""
    pass
```

---

## 6. 实现优先级与里程碑

### 6.1 MVP阶段（必须功能）
1. 命令行参数解析（FR-001）
2. 内置模板系统（FR-002）
3. 文件复制与跳过逻辑（FR-003）
4. 基础错误处理（FR-007）
5. 基本日志输出（FR-006）

### 6.2 阶段二（增强功能）
1. .gitignore规则管理（FR-004）
2. 模板变量替换（FR-005）
3. 用户级配置框架（FR-008）

### 6.3 阶段三（优化功能）
1. 性能优化
2. 更多语言支持
3. 用户自定义模板

---

## 7. 测试策略

### 7.1 测试层次
1. **单元测试**: 测试每个独立模块的功能
2. **集成测试**: 测试模块间的协作
3. **端到端测试**: 测试完整的命令行工作流

### 7.2 测试重点
- 表格驱动测试用于核心逻辑（如文件复制、变量替换）
- 使用临时目录进行文件系统测试
- 模拟用户权限场景
- 边界条件测试（空目录、超大文件、特殊字符等）

### 7.3 测试覆盖率目标
- 核心逻辑: ≥90%
- 整体项目: ≥80%

---

## 8. 风险与缓解措施

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 跨平台兼容性问题 | 高 | 中 | 使用`pathlib`替代字符串路径操作，在CI中测试多平台 |
| 文件权限问题 | 高 | 低 | 提前检查目录可写性，提供清晰的错误信息 |
| 模板目录损坏 | 中 | 低 | 验证模板完整性，提供模板修复工具 |
| 性能问题 | 低 | 低 | 使用迭代器处理大目录，限制递归深度 |
| 用户配置冲突 | 中 | 中 | 使用"跳过已存在"策略，不覆盖用户现有配置 |

---

## 9. 附录

### 9.1 参考文档
1. [Python 3.11 标准库文档](https://docs.python.org/3.11/library/)
2. [PEP 8 -- Python代码风格指南](https://peps.python.org/pep-0008/)
3. [Conventional Commits规范](https://www.conventionalcommits.org/)

### 9.2 决策记录
1. **不使用外部依赖**: 遵循简单性原则，仅使用标准库
2. **使用pathlib而非os.path**: 提供更好的跨平台兼容性
3. **使用dataclass而非普通类**: 简化数据容器定义
4. **表格驱动测试优先**: 提高测试覆盖率和可维护性

---

**方案批准**:
□ 首席架构师
□ 技术负责人
□ 产品负责人

**日期**: 2026-03-21