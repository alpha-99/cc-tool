# cc-tool 规范文档
# 版本: 0.1.1

## 概述

`cc-tool` 是一个命令行工具，用于将 Claude Code 配置文件自动初始化到指定项目中。它根据项目使用的编程语言，将对应的配置文件模板复制到项目目录中，帮助开发者快速建立与 Claude Code 的协作环境。

## 核心原则

本工具的设计与实现严格遵循项目宪法：
1. **简单性原则**: 只实现本规范中明确要求的功能。
2. **测试先行铁律**: 所有功能必须先编写失败的测试。
3. **明确性原则**: 显式错误处理，无全局变量，代码清晰易读。

## 功能规格

### 1. 输入参数

工具通过命令行参数接收输入：

```
cc-tool [OPTIONS] PROJECT_DIR LANGUAGE
```

- `PROJECT_DIR`: 目标项目目录的路径（绝对或相对路径）
- `LANGUAGE`: 编程语言类型（字符串，不区分大小写）

**支持的编程语言类型**（初始版本）:
- `python`
- `javascript` (或 `js`)
- `go`
- `rust`
- `java`

### 2. 模板系统

#### 2.1 模板结构

**MVP阶段**：仅支持内置模板。用户自定义模板功能将在未来版本中实现。

模板文件存储在工具包内的 `templates/<language>/` 目录。

每个语言模板目录应包含以下文件和目录：
- `.claude/` 目录及其子目录：
  - `settings.json` - Claude Code 权限配置
  - `agents/` - 自定义Agent定义（可选，空目录）
  - `commands/` - 自定义命令定义（可选，空目录）
  - `hooks/` - 自定义钩子定义（可选，空目录）
  - `skills/` - 自定义技能定义（可选，空目录）
- `CLAUDE.md` - 项目级指令文档
- `constitution.md` - 项目宪法（可选）
- `specs/` 目录 - 用于存放项目规范文档（可选，空目录）

#### 2.2 内置模板

工具内置以下语言的默认模板：

```
templates/
├── python/
│   ├── .claude/
│   │   ├── settings.json
│   │   ├── agents/           # 自定义Agent定义
│   │   ├── commands/         # 自定义命令定义
│   │   ├── hooks/            # 自定义钩子定义
│   │   └── skills/           # 自定义技能定义
│   ├── CLAUDE.md
│   ├── constitution.md
│   └── specs/                # 项目规范文档目录
├── javascript/
│   ├── .claude/
│   │   ├── settings.json
│   │   ├── agents/
│   │   ├── commands/
│   │   ├── hooks/
│   │   └── skills/
│   ├── CLAUDE.md
│   ├── constitution.md
│   └── specs/
├── go/
├── rust/
└── java/
```

#### 2.3 模板查找顺序

当用户指定语言类型 `LANGUAGE` 时，工具查找内置模板目录：
- 工具内置的 `templates/<LANGUAGE>/`

如果找不到对应语言的模板目录，工具应报错并退出。

**注意**：用户自定义模板功能将在未来版本中实现。当前MVP阶段仅支持内置模板。

#### 2.4 .gitignore 规则

每个语言模板应包含一个 `.gitignore` 文件（或确保目标项目的 `.gitignore` 包含以下规则），以避免将敏感或本地配置提交到版本控制：

```
# Claude Code 本地配置
.claude/settings.local.json

# IDE 配置目录
.vscode/
.idea/

# 操作系统文件
*.DS_Store

# 项目生成目录（根据语言不同）
__pycache__/
*.pyc
node_modules/
target/
dist/
build/
```

工具在复制模板文件时，应检查目标项目是否已有 `.gitignore` 文件。如果不存在，则创建并添加上述规则；如果已存在，则应确保包含上述规则（可追加到文件末尾）。

#### 2.5 模板变量替换

模板文件支持变量替换功能，允许在模板内容中使用占位符，在复制到目标项目时替换为实际值。

**支持的变量**：
- `{{PROJECT_NAME}}`: 项目名称（从目标目录名自动提取）
- `{{PROJECT_DIR}}`: 项目目录的绝对路径
- `{{LANGUAGE}}`: 编程语言类型

**替换规则**：
- 变量格式为双大括号包围：`{{VARIABLE_NAME}}`
- 所有模板文件（包括`.json`、`.md`、`.txt`等文本文件）中的变量都会被替换
- 二进制文件（如图片、压缩包等）不进行变量替换

**示例**：
模板文件 `CLAUDE.md` 中包含：
```
# {{PROJECT_NAME}} 项目配置
```

当复制到名为 `my-awesome-project` 的目录时，会被替换为：
```
# my-awesome-project 项目配置
```

### 3. 文件复制行为

#### 3.1 复制规则

- 将模板目录中的所有文件和子目录递归复制到 `PROJECT_DIR` 中
- 保持原始目录结构（如 `.claude/settings.json` 应复制为 `<PROJECT_DIR>/.claude/settings.json`）
- **跳过已存在的文件**：如果目标文件已存在，不执行任何操作（不覆盖、不修改）
- 创建必要的父目录（如 `.claude/` 目录）

#### 3.2 符号链接处理

模板目录中的符号链接应作为普通文件复制（不保持符号链接属性）。

### 4. 输出与日志

工具默认输出详细的操作日志：

```
$ cc-tool ./myproject python
[INFO] 正在初始化项目: ./myproject
[INFO] 使用语言模板: python
[INFO] 复制: .claude/settings.json → ./myproject/.claude/settings.json
[INFO] 复制: CLAUDE.md → ./myproject/CLAUDE.md
[INFO] 复制: constitution.md → ./myproject/constitution.md
[INFO] 完成！共复制 3 个文件。
```

如果文件已存在，应记录跳过：

```
[INFO] 跳过已存在文件: ./myproject/CLAUDE.md
```

### 5. 错误处理

工具必须显式处理以下错误情况：

1. **目录不存在**: `PROJECT_DIR` 不存在或不是目录
2. **权限不足**: 无法读取模板目录或写入目标目录
3. **语言不支持**: `LANGUAGE` 参数不被支持
4. **模板缺失**: 找不到对应语言的模板目录
5. **文件系统错误**: 复制过程中发生 I/O 错误

错误信息应清晰明确，帮助用户诊断问题：

```
[ERROR] 目标目录不存在: /path/to/nonexistent
[ERROR] 不支持的语言类型: ruby (支持的语言: python, javascript, go, rust, java)
[ERROR] 找不到模板目录: 语言 'python' 的模板不存在
```

所有错误都应通过适当的异常捕获处理，避免程序崩溃时输出堆栈跟踪（除非使用 `--debug` 标志）。

### 6. 命令行选项

```
用法: cc-tool [OPTIONS] PROJECT_DIR LANGUAGE

选项:
  --help, -h          显示帮助信息
  --version, -v       显示版本信息
  --list-languages, -l 列出所有支持的语言类型
  --list-templates, -t 列出所有可用的模板（包括自定义模板）
  --dry-run, -n       预览将要执行的操作，但不实际复制文件
  --verbose, -V       输出更详细的调试信息（默认已启用详细输出）
  --quiet, -q         静默模式，只输出错误信息
```

### 7. 配置系统

#### 7.1 用户级框架初始化

工具在首次运行时，应检查并初始化用户级的Claude Code配置框架（如果不存在）：

**检查的目录和文件**：
- `~/.claude/` 目录
- `~/.claude/commands/` 目录
- `~/.claude/skills/` 目录
- `~/.claude/agents/` 目录
- `~/.claude/settings.json` 文件
- `~/.claude/CLAUDE.md` 文件

**初始化行为**：
- 如果目录不存在，创建空目录
- 如果文件不存在，创建包含基本注释的模板文件
- 如果目录或文件已存在，跳过（不覆盖、不修改）

**用户配置目录**：
- 工具配置目录: `~/.config/cc-tool/`（未来版本使用）
- 用户模板目录: `~/.config/cc-tool/templates/`（未来版本使用）

配置文件暂不实现，留待未来扩展。

### 8. 非功能需求

#### 8.1 性能
- 能快速处理包含少量文件的项目
- 递归复制时避免深度嵌套导致的性能问题

#### 8.2 可维护性
- 代码模块化，便于添加新的语言支持
- 清晰的错误处理逻辑

#### 8.3 可测试性
- 所有核心功能都必须有单元测试
- 优先使用表格驱动测试（Table-Driven Tests）
- 测试覆盖率不低于 80%

### 9. 测试策略

#### 9.1 单元测试
对以下组件进行单元测试：
- 命令行参数解析
- 模板查找逻辑
- 文件复制逻辑
- 错误处理逻辑

#### 9.2 集成测试
测试完整的命令行工作流程：
```
给定：一个空项目目录
当：运行 cc-tool <dir> python
那么：目录中应包含预期的配置文件
```

#### 9.3 表格驱动测试用例示例
```python
test_cases = [
    {
        "name": "复制新文件",
        "template_files": [".claude/settings.json"],
        "existing_files": [],
        "expected_copied": [".claude/settings.json"],
        "expected_skipped": []
    },
    {
        "name": "跳过已存在文件",
        "template_files": ["CLAUDE.md"],
        "existing_files": ["CLAUDE.md"],
        "expected_copied": [],
        "expected_skipped": ["CLAUDE.md"]
    },
    # ... 更多测试用例
]
```

### 10. 未来扩展可能性

1. **配置文件**: 支持 `~/.config/cc-tool/config.toml` 配置默认行为
2. **更多语言**: 扩展支持 C++, C#, PHP, Ruby 等
3. **框架特定模板**: 支持 Django, React, Vue 等框架的特定配置
4. **用户自定义模板**: 支持 `~/.config/cc-tool/templates/<language>/` 目录的用户自定义模板（覆盖内置模板）
5. **批量操作**: 支持一次性初始化多个项目目录
6. **模板变量增强**: 支持更多变量类型和自定义变量

### 附录

#### A. 语言别名映射

为方便使用，支持以下语言别名：
- `js` → `javascript`
- `py` → `python`
- `golang` → `go`

#### B. 内置模板内容示例

**python/.claude/settings.json**:
```json
{
  "permissions": {
    "defaultMode": "plan",
    "allow": [
      "Read(*.py)",
      "Read(pyproject.toml)",
      "Read(requirements.txt)",
      "Read(requirements/*.txt)",
      "Read(setup.py)",
      "Read(Pipfile)",
      "Read(Pipfile.lock)",
      "Read(README.md)",
      "Read(constitution.md)",
      "Read(specs/**)",
      "Grep",
      "Glob",
      "LS",
      "Bash(python:version)",
      "Bash(pip:list:*)",
      "Bash(python:build:*)",
      "Bash(pytest:run:*)",
      "Bash(black:*)",
      "Bash(isort:*)",
      "Bash(flake8:*)",
      "Bash(mypy:*)"
    ],
    "ask": [
      "Write",
      "Edit",
      "MultiEdit",
      "Bash(pip:install:*)",
      "Bash(pip:freeze:*)",
      "Bash(git:add:*)",
      "Bash(git:commit:*)"
    ],
    "deny": [
      "Read(./.env*)",
      "Read(*.pem)",
      "Read(*.key)",
      "Bash(rm:*)",
      "Bash(git:push:*)",
      "WebFetch"
    ]
  }
}
```

**其他语言的模板**应有针对该语言的合理默认权限设置。

---
*文档版本: 0.1.1*
*最后更新: 2026-03-20*