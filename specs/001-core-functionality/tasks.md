# cc-tool 开发任务清单
## 版本: 1.0.0
## 最后更新: 2026-03-21

## 概述
本文件基于 `spec.md` 和 `plan.md` 将技术方案分解为原子化、有依赖关系的任务。任务遵循TDD原则：每个功能模块先编写测试，再实现代码。

## 任务标记说明
- `[P]`: 可并行执行的任务（无依赖关系）
- `[D:任务ID]`: 依赖的任务ID
- `(TDD)`: 测试先行任务
- `(实现)`: 对应测试的实现任务

## 阶段划分

### Phase 1: Foundation (数据结构定义)
**目标**: 定义项目核心数据结构和常量，为其他模块提供基础类型。

| 任务ID | 任务描述 | 依赖 | 并行标记 | 文件路径 | 验收标准 |
|--------|----------|------|----------|----------|----------|
| **1.1** | **(TDD) 创建数据结构测试** | 无 | [P] | `tests/test_models.py` | 1. 包含对TemplateConfig、ProjectContext、CopyResult、GitignoreRule的测试用例<br>2. 使用表格驱动测试风格<br>3. 测试dataclass的初始化和属性访问 |
| **1.2** | **(实现) 创建models.py定义核心数据结构** | 1.1 | | `cc_tool/models.py` | 1. 定义TemplateConfig、ProjectContext、CopyResult、GitignoreRule四个dataclass<br>2. 使用typing进行类型注解<br>3. 添加适当的文档字符串 |
| **1.3** | **(TDD) 创建常量测试** | 无 | [P] | `tests/test_constants.py` | 1. 测试SUPPORTED_LANGUAGES字典的正确性<br>2. 测试REQUIRED_TEMPLATE_FILES列表<br>3. 测试GITIGNORE_RULES结构 |
| **1.4** | **(实现) 创建constants.py定义项目常量** | 1.3 | | `cc_tool/constants.py` | 1. 定义SUPPORTED_LANGUAGES字典<br>2. 定义REQUIRED_TEMPLATE_FILES列表<br>3. 定义GITIGNORE_RULES字典结构<br>4. 添加清晰的注释说明 |
| **1.5** | **创建模板目录结构** | 无 | [P] | `templates/` 目录 | 1. 创建templates/python/.claude/settings.json基础模板<br>2. 创建templates/python/CLAUDE.md基础模板<br>3. 创建其他语言(python, javascript, go, rust, java)的目录结构<br>4. 确保每个语言模板包含必需文件 |

### Phase 2: 命令解析
**目标**: 实现命令行参数解析和基础工具模块（错误处理、日志）。

| 任务ID | 任务描述 | 依赖 | 并行标记 | 文件路径 | 验收标准 |
|--------|----------|------|----------|----------|----------|
| **2.1** | **(TDD) 创建错误类型测试** | 1.2 | [P] | `tests/test_errors.py` | 1. 测试所有自定义异常类的继承关系<br>2. 测试异常消息的格式和内容<br>3. 测试异常抛出和捕获行为 |
| **2.2** | **(实现) 创建errors.py定义自定义异常** | 2.1 | | `cc_tool/errors.py` | 1. 定义CCToolError基类<br>2. 定义ProjectDirectoryError等7个具体异常类<br>3. 每个异常类有清晰的文档字符串 |
| **2.3** | **(TDD) 创建日志系统测试** | 无 | [P] | `tests/test_logger.py` | 1. 测试setup_logger函数的verbose/quiet参数<br>2. 测试log_info、log_warning、log_error、log_debug的输出格式<br>3. 测试不同日志级别的过滤行为 |
| **2.4** | **(实现) 创建logger.py实现日志系统** | 2.3 | | `cc_tool/logger.py` | 1. 实现setup_logger函数，配置logging模块<br>2. 实现log_info等四个日志函数<br>3. 支持verbose和quiet模式<br>4. 日志格式符合spec要求（如[INFO]前缀） |
| **2.5** | **(TDD) 创建命令行解析测试** | 1.4, 2.2, 2.4 | | `tests/test_cli.py` | 1. 使用表格驱动测试命令行参数组合<br>2. 测试必需参数(PROJECT_DIR, LANGUAGE)解析<br>3. 测试可选参数(--help, --version等)<br>4. 测试语言别名映射和不区分大小写<br>5. 测试参数验证和错误处理 |
| **2.6** | **(实现) 创建cli.py实现命令行解析** | 2.5 | | `cc_tool/cli.py` | 1. 使用argparse解析命令行参数<br>2. 实现所有必需和可选参数<br>3. 实现语言别名映射（js→javascript等）<br>4. 参数验证和错误提示<br>5. 帮助信息和版本信息输出 |

### Phase 3: 模板处理
**目标**: 实现模板查找、验证和变量替换功能。

| 任务ID | 任务描述 | 依赖 | 并行标记 | 文件路径 | 验收标准 |
|--------|----------|------|----------|----------|----------|
| **3.1** | **(TDD) 创建模板查找测试** | 1.2, 1.4, 2.2 | [P] | `tests/test_template.py` | 1. 测试find_template函数对支持语言的查找<br>2. 测试语言别名映射<br>3. 测试不支持语言的异常抛出<br>4. 测试模板目录不存在的情况<br>5. 使用表格驱动测试 |
| **3.2** | **(实现) 创建template.py实现模板查找** | 3.1 | | `cc_tool/template.py` | 1. 实现find_template函数，返回TemplateConfig<br>2. 实现validate_template函数验证模板完整性<br>3. 正确处理语言别名和不区分大小写<br>4. 抛出自定义异常（LanguageNotSupportedError等） |
| **3.3** | **(TDD) 创建变量替换测试** | 1.2 | [P] | `tests/test_variables.py` | 1. 测试{{PROJECT_NAME}}、{{PROJECT_DIR}}、{{LANGUAGE}}变量替换<br>2. 测试多变量同时替换<br>3. 测试二进制文件不进行替换<br>4. 测试文件编码处理<br>5. 使用表格驱动测试 |
| **3.4** | **(实现) 创建variables.py实现变量替换** | 3.3 | | `cc_tool/variables.py` | 1. 实现replace_variables_in_file函数<br>2. 支持三种变量替换<br>3. 自动检测文本文件和二进制文件<br>4. 正确处理文件编码<br>5. 抛出自定义异常（VariableReplaceError） |

### Phase 4: 文件copy处理
**目标**: 实现文件复制、.gitignore管理和用户级配置初始化。

| 任务ID | 任务描述 | 依赖 | 并行标记 | 文件路径 | 验收标准 |
|--------|----------|------|----------|----------|----------|
| **4.1** | **(TDD) 创建文件操作测试** | 1.2, 2.2, 3.4 | [P] | `tests/test_file_ops.py` | 1. 测试copy_template_files函数的复制行为<br>2. 测试跳过已存在文件的逻辑<br>3. 测试递归复制和目录创建<br>4. 测试dry-run预览模式<br>5. 测试符号链接处理<br>6. 使用表格驱动测试（参考spec附录示例） |
| **4.2** | **(实现) 创建file_ops.py实现文件操作** | 4.1 | | `cc_tool/file_ops.py` | 1. 实现copy_template_files函数，返回CopyResult<br>2. 实现递归复制，保持目录结构<br>3. 跳过已存在文件（不覆盖）<br>4. 自动创建父目录<br>5. 支持dry-run模式<br>6. 符号链接作为普通文件复制 |
| **4.3** | **(TDD) 创建.gitignore管理测试** | 1.4, 2.2 | [P] | `tests/test_gitignore.py` | 1. 测试.gitignore文件创建<br>2. 测试规则追加（不重复）<br>3. 测试不同语言的特定规则<br>4. 测试文件已存在但规则缺失的情况<br>5. 使用表格驱动测试 |
| **4.4** | **(实现) 创建gitignore.py实现.gitignore管理** | 4.3 | | `cc_tool/gitignore.py` | 1. 实现manage_gitignore函数<br>2. 创建.gitignore文件（如果不存在）<br>3. 追加缺失规则（如果文件存在）<br>4. 避免重复规则<br>5. 包含语言特定规则<br>6. 抛出自定义异常（GitignoreError） |
| **4.5** | **(TDD) 创建用户配置测试** | 2.2 | [P] | `tests/test_user_config.py` | 1. 测试~/.claude/目录结构初始化<br>2. 测试跳过已存在目录和文件<br>3. 测试基本配置文件的创建<br>4. 测试跨平台路径处理 |
| **4.6** | **(实现) 创建user_config.py实现用户配置初始化** | 4.5 | | `cc_tool/user_config.py` | 1. 实现initialize_user_config函数<br>2. 创建~/.claude/及其子目录<br>3. 创建基础配置文件（含注释模板）<br>4. 跳过已存在的目录和文件（不覆盖）<br>5. 抛出自定义异常（UserConfigError） |

### Phase 5: cli入口集成
**目标**: 实现核心协调逻辑、主入口点和端到端测试。

| 任务ID | 任务描述 | 依赖 | 并行标记 | 文件路径 | 验收标准 |
|--------|----------|------|----------|----------|----------|
| **5.1** | **(TDD) 创建核心逻辑测试** | 1.2, 2.2, 2.4, 2.6, 3.2, 3.4, 4.2, 4.4, 4.6 | | `tests/test_core.py` | 1. 测试initialize_project函数的完整流程<br>2. 测试verbose、quiet、dry-run参数传递<br>3. 测试错误处理链（目录不存在、权限不足等）<br>4. 测试CopyResult统计信息<br>5. 使用表格驱动测试 |
| **5.2** | **(实现) 创建core.py实现核心协调逻辑** | 5.1 | | `cc_tool/core.py` | 1. 实现initialize_project函数，协调所有模块<br>2. 调用template.find_template查找模板<br>3. 调用file_ops.copy_template_files复制文件<br>4. 调用gitignore.manage_gitignore管理.gitignore<br>5. 调用user_config.initialize_user_config初始化用户配置<br>6. 处理所有异常并提供清晰错误信息<br>7. 返回CopyResult统计结果 |
| **5.3** | **(实现) 创建__main__.py实现CLI入口** | 2.6, 5.2 | | `cc_tool/__main__.py` | 1. 导入cli和core模块<br>2. 解析命令行参数<br>3. 调用core.initialize_project<br>4. 处理异常并输出友好错误信息<br>5. 设置适当的退出码 |
| **5.4** | **(TDD) 创建端到端集成测试** | 所有模块 | | `tests/integration/test_end_to_end.py` | 1. 测试完整命令行工作流<br>2. 使用临时目录模拟真实场景<br>3. 测试spec中的所有验收标准（AC-001到AC-009）<br>4. 验证生成的文件和目录结构<br>5. 验证变量替换结果<br>6. 验证.gitignore规则 |
| **5.5** | **创建项目配置文件** | 无 | [P] | `pyproject.toml` | 1. 配置项目元数据（名称、版本、描述）<br>2. 配置入口点（console_scripts）<br>3. 配置构建后端（setuptools）<br>4. 配置Python版本要求（>=3.11） |
| **5.6** | **创建基础文档** | 无 | [P] | `README.md` | 1. 项目概述和安装说明<br>2. 基本使用示例<br>3. 支持的语言列表<br>4. 命令行参数说明 |

## 任务依赖关系图

```
Phase 1:
1.1 → 1.2
1.3 → 1.4
1.5 (独立)

Phase 2:
1.2 → 2.1 → 2.2
1.4,2.2,2.4 → 2.5 → 2.6
2.3 → 2.4

Phase 3:
1.2,1.4,2.2 → 3.1 → 3.2
1.2 → 3.3 → 3.4

Phase 4:
1.2,2.2,3.4 → 4.1 → 4.2
1.4,2.2 → 4.3 → 4.4
2.2 → 4.5 → 4.6

Phase 5:
(所有前置模块) → 5.1 → 5.2
2.6,5.2 → 5.3
(所有模块) → 5.4
5.5,5.6 (独立)
```

## 并行执行建议

### 可并行执行的批次：

**批次1** (Phase 1基础):
- 任务1.1, 1.3, 1.5 可并行执行

**批次2** (Phase 2基础):
- 任务2.1, 2.3 可并行执行（依赖Phase 1完成）

**批次3** (Phase 3):
- 任务3.1, 3.3 可并行执行（依赖Phase 1,2基础）

**批次4** (Phase 4基础):
- 任务4.1, 4.3, 4.5 可并行执行（依赖相应前置任务）

**批次5** (Phase 5独立任务):
- 任务5.5, 5.6 可随时并行执行

## 测试策略执行指南

1. **表格驱动测试优先**: 任务1.1, 1.3, 2.5, 3.1, 3.3, 4.1, 4.3, 4.5, 5.1, 5.4必须使用表格驱动测试
2. **真实文件系统测试**: 涉及文件操作的任务（4.x, 5.4）使用临时目录，避免污染实际文件系统
3. **异常测试覆盖**: 所有实现任务必须测试异常情况，验证错误信息清晰明确
4. **跨平台考虑**: 使用pathlib进行路径操作，确保Linux/macOS/Windows兼容性

## 完成标准

1. **所有任务完成**: 每个任务对应的文件已创建并通过验收标准
2. **测试通过**: 所有测试文件执行通过，无失败用例
3. **代码质量**: 符合Pythonic风格，有适当的类型注解和文档字符串
4. **集成验证**: 端到端测试（5.4）验证所有spec中的验收标准

## 附录：验收标准映射

| Spec验收标准 | 对应任务 | 测试验证点 |
|--------------|----------|------------|
| AC-001 (命令行参数解析) | 2.5, 2.6, 5.4 | test_cli.py, test_end_to_end.py |
| AC-002 (模板查找与验证) | 3.1, 3.2, 5.4 | test_template.py, test_end_to_end.py |
| AC-003 (文件复制行为) | 4.1, 4.2, 5.4 | test_file_ops.py, test_end_to_end.py |
| AC-004 (.gitignore规则) | 4.3, 4.4, 5.4 | test_gitignore.py, test_end_to_end.py |
| AC-005 (模板变量替换) | 3.3, 3.4, 5.4 | test_variables.py, test_end_to_end.py |
| AC-006 (输出与日志) | 2.3, 2.4, 5.4 | test_logger.py, test_end_to_end.py |
| AC-007 (错误处理) | 2.1, 2.2, 所有实现任务 | test_errors.py, 各模块异常测试 |
| AC-008 (用户级框架) | 4.5, 4.6, 5.4 | test_user_config.py, test_end_to_end.py |
| AC-009 (集成测试场景) | 5.4 | test_end_to_end.py |

---
**任务清单批准**:
□ 技术组长
□ 首席架构师

**日期**: 2026-03-21