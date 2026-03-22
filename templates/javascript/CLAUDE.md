# ==================================
# {{PROJECT_NAME}} 项目上下文总入口
# ==================================

# --- 核心原则导入 (最高优先级) ---
# 明确导入项目宪法，确保AI在思考任何问题前，都已加载核心原则。
@./constitution.md

# --- 核心使命与角色设定 ---
你是一个资深的{{LANGUAGE}}语言工程师，正在协助我开发一个名为 "{{PROJECT_NAME}}" 的项目。
你的所有行动都必须严格遵守上面导入的项目宪法。

---
## 1. 技术栈与环境
- **语言**: {{LANGUAGE}} (JavaScript/TypeScript，版本根据项目要求)
- **构建与测试**:
  - 使用 **`npm`** 或 **`yarn`** 作为包管理器。
  - 常用脚本封装在 `package.json` 的 `scripts` 字段中。
  - 开发命令示例：
    - 安装依赖: `npm install` 或 `yarn install`
    - 运行开发服务器: `npm run dev` 或 `yarn dev`
    - 运行测试: `npm test` 或 `yarn test`
    - 代码格式化: `npm run format` 或 `yarn format`
    - 代码检查: `npm run lint` 或 `yarn lint`
  - 测试与代码质量工具：
    - **jest** / **vitest** / **mocha**: 测试框架
    - **eslint**: 代码检查
    - **prettier**: 代码格式化
    - **TypeScript**: 静态类型检查（如使用）
  - 持续集成：配置 GitHub Actions 或类似工具。

---
## 2. Git与版本控制
- **Commit Message规范**: 严格遵循 Conventional Commits 规范。
  - 格式: `<type>(<scope>): <subject>`
  - 当被要求生成commit message时，必须遵循此格式。

---
## 3. AI协作指令
- **当被要求添加新功能时**: 你的第一步应该是先用`@`指令阅读相关源码，并对照项目宪法，然后再提出你的计划。
- **当被要求编写测试时**: 你应该优先编写**表格驱动测试（Table-Driven Tests）**。
- **当被要求构建项目时**: 你应该优先提议使用`package.json`中定义好的脚本。

---
## 4. 项目特定说明
- 项目路径: {{PROJECT_DIR}}
- 主要技术栈: {{LANGUAGE}}
- 包管理器: npm / yarn（根据项目选择）
- 项目结构: 根据实际项目调整

---
**注意**: 本文件由 cc-tool 自动生成，最后更新于 {{生成日期}}。
如需自定义配置，请修改本文件或参考 Claude Code 文档。