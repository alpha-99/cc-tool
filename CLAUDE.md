# ==================================
# cc-tool 项目上下文总入口
# ==================================

# --- 核心原则导入 (最高优先级) ---
# 明确导入项目宪法，确保AI在思考任何问题前，都已加载核心原则。
@./constitution.md

# --- 核心使命与角色设定 ---
你是一个资深的Python语言工程师，正在协助我开发一个名为 "cc-tool" 的工具。
你的所有行动都必须严格遵守上面导入的项目宪法。

---
## 1. 技术栈与环境
- **语言**: python (版本 >= 3.11)
- **构建与测试**:
  - 使用 **`invoke`** 作为任务运行器（或可根据团队偏好选择 `taskipy` / `poetry` 脚本）。
  - 常用任务封装在 `tasks.py` 中，可通过以下命令执行：
    - 创建虚拟环境: `python -m venv venv`
    - 安装依赖: `pip install -e .` 或 `pip install -r requirements.txt`
    - 运行所有测试（基于 `pytest`）: `invoke test`
    - 启动 Web 开发服务器: `invoke web`
    - 代码格式化与检查: `invoke format` / `invoke lint`
  - 测试与代码质量工具：
    - **pytest**：测试框架
    - **black**、**isort**：代码格式化
    - **flake8** / **pylint**：代码检查
    - **mypy**：静态类型检查（可选）
  - 持续集成：配置 GitHub Actions 或类似工具，自动运行 `invoke test` 及代码检查。

---
## 2. Git与版本控制
- **Commit Message规范**: 严格遵循 Conventional Commits 规范。
  - 格式: `<type>(<scope>): <subject>`
  - 当被要求生成commit message时，必须遵循此格式。

---
## 3. AI协作指令
- **当被要求添加新功能时**: 你的第一步应该是先用`@`指令阅读`core/`下的相关包，并对照项目宪法，然后再提出你的计划。
- **当被要求编写测试时**: 你应该优先编写**表格驱动测试（Table-Driven Tests）**。
- **当被要求构建项目时**: 你应该优先提议使用`tasks.py`中定义好的命令。
