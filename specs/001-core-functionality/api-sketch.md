# API 接口设计草图
## 版本: 1.0.0
## 最后更新: 2026-03-20

---

## 概述

本文档描述了 `cc-tool` 核心功能的公共 API 接口设计。遵循项目宪法原则，所有接口都追求简洁、明确和模块化。

## 设计原则

1. **显式依赖注入**: 所有依赖通过函数参数传递，无全局状态
2. **单一职责**: 每个函数/类有明确的单一职责
3. **错误处理优先**: 使用自定义异常类型，错误信息清晰
4. **接口简洁**: 保持函数签名最小化，便于测试和组合

## 主要接口

### 1. 命令行接口 (CLI)

```python
# cc_tool/cli.py

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """
    解析命令行参数。

    Args:
        argv: 命令行参数列表，默认使用 sys.argv[1:]

    Returns:
        argparse.Namespace: 解析后的参数对象

    Raises:
        CLIError: 参数解析失败时抛出
    """
    pass

def main() -> int:
    """
    主入口点函数。

    Returns:
        int: 退出码 (0表示成功，非0表示失败)
    """
    pass
```

### 2. 模板系统

```python
# cc_tool/template.py

class TemplateError(Exception):
    """模板相关错误的基类"""
    pass

class TemplateNotFoundError(TemplateError):
    """模板未找到错误"""
    pass

def find_template(language: str, template_base_dir: Optional[Path] = None) -> Path:
    """
    根据语言名称查找模板目录。

    Args:
        language: 编程语言名称（不区分大小写）
        template_base_dir: 模板基础目录，默认为内置模板目录

    Returns:
        Path: 找到的模板目录路径

    Raises:
        TemplateNotFoundError: 找不到对应语言的模板时抛出
        ValueError: language参数无效时抛出
    """
    pass

def normalize_language(language: str) -> str:
    """
    规范化语言名称（处理别名和大小写）。

    Args:
        language: 原始语言名称

    Returns:
        str: 规范化的语言名称

    Examples:
        >>> normalize_language("js")
        "javascript"
        >>> normalize_language("PYTHON")
        "python"
    """
    pass

def get_supported_languages() -> List[str]:
    """
    获取支持的语言列表。

    Returns:
        List[str]: 支持的语言名称列表
    """
    pass
```

### 3. 文件操作

```python
# cc_tool/file_ops.py

class FileOperationError(Exception):
    """文件操作错误的基类"""
    pass

class DestinationExistsError(FileOperationError):
    """目标文件已存在错误（用于跳过逻辑）"""
    pass

def copy_template(
    template_dir: Path,
    destination_dir: Path,
    *,
    skip_existing: bool = True,
    variables: Optional[Dict[str, str]] = None,
    dry_run: bool = False
) -> Tuple[List[Path], List[Path]]:
    """
    将模板目录复制到目标目录。

    Args:
        template_dir: 模板源目录
        destination_dir: 目标目录
        skip_existing: 是否跳过已存在的文件（默认True）
        variables: 模板变量替换字典
        dry_run: 是否只预览不实际执行（默认False）

    Returns:
        Tuple[List[Path], List[Path]]: (成功复制的文件列表, 跳过的文件列表)

    Raises:
        FileOperationError: 文件操作失败时抛出
        PermissionError: 权限不足时抛出
    """
    pass

def process_file_variables(
    source_path: Path,
    destination_path: Path,
    variables: Dict[str, str]
) -> None:
    """
    处理单个文件的变量替换。

    Args:
        source_path: 源文件路径
        destination_path: 目标文件路径
        variables: 变量替换字典

    Raises:
        FileOperationError: 文件处理失败时抛出
    """
    pass

def is_binary_file(file_path: Path) -> bool:
    """
    判断文件是否为二进制文件。

    Args:
        file_path: 文件路径

    Returns:
        bool: True表示为二进制文件，False表示为文本文件
    """
    pass
```

### 4. .gitignore 管理

```python
# cc_tool/gitignore.py

def ensure_gitignore_rules(
    project_dir: Path,
    rules: List[str],
    *,
    dry_run: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    确保项目的.gitignore文件包含指定规则。

    Args:
        project_dir: 项目目录
        rules: 需要确保的规则列表
        dry_run: 是否只预览不实际执行

    Returns:
        Tuple[bool, Optional[str]]:
            - bool: 是否进行了修改（True表示创建或追加了规则）
            - Optional[str]: 修改描述，dry_run时为预览描述

    Raises:
        FileOperationError: 文件操作失败时抛出
    """
    pass

def get_default_gitignore_rules(language: str) -> List[str]:
    """
    获取指定语言的默认.gitignore规则。

    Args:
        language: 编程语言名称

    Returns:
        List[str]: 该语言的默认.gitignore规则列表
    """
    pass
```

### 5. 变量系统

```python
# cc_tool/variables.py

class VariableError(Exception):
    """变量相关错误的基类"""
    pass

def extract_project_name(project_dir: Path) -> str:
    """
    从项目目录路径提取项目名称。

    Args:
        project_dir: 项目目录路径

    Returns:
        str: 项目名称（目录名的basename）

    Raises:
        ValueError: project_dir无效时抛出
    """
    pass

def build_template_variables(
    project_dir: Path,
    language: str,
    extra_variables: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    构建模板变量字典。

    Args:
        project_dir: 项目目录路径
        language: 编程语言名称
        extra_variables: 额外的自定义变量

    Returns:
        Dict[str, str]: 完整的变量字典，包含：
            - PROJECT_NAME: 项目名称
            - PROJECT_DIR: 项目目录绝对路径
            - LANGUAGE: 编程语言
            - 所有extra_variables中的变量
    """
    pass

def replace_variables_in_content(
    content: str,
    variables: Dict[str, str]
) -> str:
    """
    在文本内容中替换变量占位符。

    Args:
        content: 原始文本内容
        variables: 变量替换字典

    Returns:
        str: 替换后的文本内容
    """
    pass
```

### 6. 用户级框架初始化

```python
# cc_tool/user_config.py

class UserConfigError(Exception):
    """用户配置错误的基类"""
    pass

def ensure_user_framework(
    user_home: Optional[Path] = None,
    *,
    dry_run: bool = False
) -> Tuple[List[Path], List[Path]]:
    """
    确保用户级Claude Code框架目录结构存在。

    Args:
        user_home: 用户home目录，默认为Path.home()
        dry_run: 是否只预览不实际执行

    Returns:
        Tuple[List[Path], List[Path]]: (创建的目录列表, 创建的文件列表)

    Raises:
        UserConfigError: 配置初始化失败时抛出
        PermissionError: 权限不足时抛出
    """
    pass

def get_user_claude_dir(user_home: Optional[Path] = None) -> Path:
    """
    获取用户级.claude目录路径。

    Args:
        user_home: 用户home目录，默认为Path.home()

    Returns:
        Path: 用户级.claude目录路径
    """
    pass
```

### 7. 日志系统

```python
# cc_tool/logger.py

class LogLevel(Enum):
    """日志级别枚举"""
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    DEBUG = "debug"

class Logger:
    """
    日志记录器，支持不同级别和输出目标。
    """

    def __init__(
        self,
        level: LogLevel = LogLevel.INFO,
        output_stream: Optional[TextIO] = None,
        error_stream: Optional[TextIO] = None
    ):
        """
        初始化日志记录器。

        Args:
            level: 日志级别
            output_stream: 标准输出流，默认为sys.stdout
            error_stream: 错误输出流，默认为sys.stderr
        """
        pass

    def info(self, message: str, **kwargs) -> None:
        """记录INFO级别日志"""
        pass

    def error(self, message: str, **kwargs) -> None:
        """记录ERROR级别日志"""
        pass

    def debug(self, message: str, **kwargs) -> None:
        """记录DEBUG级别日志"""
        pass

    def set_level(self, level: LogLevel) -> None:
        """设置日志级别"""
        pass
```

### 8. 错误处理

```python
# cc_tool/errors.py

class CCError(Exception):
    """cc-tool所有异常的基类"""
    pass

class CLIError(CCError):
    """命令行接口错误"""
    pass

class ConfigError(CCError):
    """配置错误"""
    pass

class TemplateError(CCError):
    """模板错误"""
    pass

class FileOperationError(CCError):
    """文件操作错误"""
    pass

def format_error_message(error: Exception, context: Optional[Dict] = None) -> str:
    """
    格式化错误信息，包含上下文信息。

    Args:
        error: 异常对象
        context: 额外的上下文信息

    Returns:
        str: 格式化的错误信息字符串
    """
    pass
```

### 9. 核心协调器

```python
# cc_tool/core.py

class CCTool:
    """
    cc-tool核心协调器，组合各个模块的功能。
    """

    def __init__(
        self,
        logger: Optional[Logger] = None,
        template_base_dir: Optional[Path] = None
    ):
        """
        初始化CCTool实例。

        Args:
            logger: 日志记录器实例，默认创建新的
            template_base_dir: 模板基础目录，默认为内置模板目录
        """
        pass

    def initialize_project(
        self,
        project_dir: Path,
        language: str,
        *,
        skip_existing: bool = True,
        dry_run: bool = False,
        init_user_framework: bool = True
    ) -> Dict[str, Any]:
        """
        初始化项目目录。

        Args:
            project_dir: 项目目录路径
            language: 编程语言名称
            skip_existing: 是否跳过已存在的文件
            dry_run: 是否只预览不实际执行
            init_user_framework: 是否初始化用户级框架

        Returns:
            Dict[str, Any]: 操作结果统计，包含：
                - copied_files: List[Path] 复制的文件列表
                - skipped_files: List[Path] 跳过的文件列表
                - gitignore_modified: bool .gitignore是否被修改
                - user_framework_created: List[Path] 创建的用户框架项

        Raises:
            CCError: 任何子错误都会转换为CCError
        """
        pass

    def list_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        pass

    def list_templates(self) -> Dict[str, List[str]]:
        """列出所有可用的模板"""
        pass
```

## 包结构设计

```
cc_tool/
├── __init__.py              # 包初始化，导出公共API
├── __main__.py             # 命令行入口点
├── cli.py                  # 命令行参数解析
├── core.py                 # 核心协调器
├── errors.py               # 自定义异常定义
├── logger.py               # 日志系统
├── template.py             # 模板查找和验证
├── file_ops.py             # 文件复制和变量替换
├── gitignore.py            # .gitignore规则管理
├── variables.py            # 变量系统
└── user_config.py          # 用户级框架初始化

templates/                  # 内置模板目录（非Python包）
├── python/
├── javascript/
├── go/
├── rust/
└── java/

tests/                      # 测试目录
├── __init__.py
├── test_cli.py
├── test_template.py
├── test_file_ops.py
├── test_gitignore.py
├── test_variables.py
├── test_user_config.py
└── integration/
    └── test_end_to_end.py
```

## 依赖关系图

```
cli.py → core.py → 所有其他模块
                ↘ template.py
                ↘ file_ops.py → variables.py
                ↘ gitignore.py
                ↘ user_config.py
                ↘ logger.py
                ↗ errors.py (所有模块都可能使用)
```

## 设计说明

1. **模块化**: 每个模块有明确的职责，便于单独测试和维护
2. **依赖注入**: 核心协调器`CCTool`接受外部依赖，便于测试和配置
3. **错误处理**: 使用自定义异常类型，错误信息包含足够上下文
4. **可测试性**: 所有函数都有明确的输入输出，无全局状态
5. **扩展性**: 模板系统设计支持未来添加用户自定义模板
6. **符合宪法**:
   - 简单性原则：只暴露必要的接口
   - 测试先行：所有接口都便于编写表格驱动测试
   - 明确性原则：函数签名清晰，错误处理显式

## 使用示例

```python
# 作为库使用
from cc_tool import CCTool, Logger

logger = Logger(level=LogLevel.INFO)
tool = CCTool(logger=logger)

try:
    result = tool.initialize_project(
        project_dir=Path("./myproject"),
        language="python",
        dry_run=False
    )
    print(f"初始化完成: 复制了{len(result['copied_files'])}个文件")
except CCError as e:
    print(f"初始化失败: {e}")
```

```bash
# 作为命令行工具使用
$ cc-tool ./myproject python
$ cc-tool --list-languages
$ cc-tool --dry-run ./myproject javascript
```