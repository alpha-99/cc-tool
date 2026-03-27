# cc-tool

一个命令行工具，用于将 Claude Code 配置文件自动初始化到指定项目中。根据项目使用的编程语言，将对应的配置文件模板复制到项目目录中，帮助开发者快速建立与 Claude Code 的协作环境。

## 安装

```bash
# 克隆仓库
git clone https://github.com/alpha-99/cc-tool.git
cd cc-tool

# 安装依赖（可选创建虚拟环境）
pip install -e .
```

## 用法

```bash
cc-tool [OPTIONS] PROJECT_DIR LANGUAGE
python3 -m cc_tool.cli --verbose /home/bhl/workspace/awesome-app python
```

## 代码审查
```shell
 /review-go-code cc-tool/
```

## 代码提交
```shell
/commit
```

**必需参数：**
- `PROJECT_DIR`：目标项目目录的路径（绝对或相对路径）
- `LANGUAGE`：编程语言类型（字符串，不区分大小写）

**选项：**
- `-h, --help`：显示帮助信息
- `-v, --version`：显示版本信息
- `-l, --list-languages`：列出支持的语言类型
- `-t, --list-templates`：列出可用模板
- `-n, --dry-run`：预览操作但不实际执行
- `-V, --verbose`：输出详细调试信息
- `-q, --quiet`：静默模式，只输出错误

## 支持的语言

初始版本支持以下编程语言：
- `python` (别名 `py`)
- `javascript` (别名 `js`)
- `go` (别名 `golang`)
- `rust`
- `java`

## 特性

- **语言特定模板**：为每种语言提供合适的 Claude Code 配置模板
- **安全文件复制**：跳过已存在的文件，避免覆盖现有配置
- **模板变量替换**：自动替换 `{{PROJECT_NAME}}`、`{{PROJECT_DIR}}`、`{{LANGUAGE}}` 等变量
- **.gitignore 管理**：自动添加 Claude Code 和 IDE 相关的忽略规则
- **详细日志输出**：清晰显示每个文件的操作状态（复制/跳过）
- **用户级配置框架初始化**：首次运行时自动创建用户级 Claude Code 配置目录
- **防御性错误处理**：显式处理目录不存在、权限不足、不支持的语言等错误

## 示例

### 初始化 Python 项目

```bash
cc-tool /path/to/myproject python
```

输出示例：
```
[INFO] 正在初始化项目: /path/to/myproject
[INFO] 使用语言模板: python
[INFO] 复制: .claude/settings.json → /path/to/myproject/.claude/settings.json
[INFO] 复制: CLAUDE.md → /path/to/myproject/CLAUDE.md
[INFO] 跳过已存在文件: /path/to/myproject/.gitignore
[INFO] 完成！共复制 3 个文件。
```

### 预览模式（不实际执行）

```bash
cc-tool --dry-run ./myproject javascript
```

### 列出支持的语言

```bash
cc-tool --list-languages
```

## 开发

## 许可证

[待添加]

## 贡献

欢迎提交 Issue 和 Pull Request。请确保所有更改都遵循项目宪法并包含相应的测试。