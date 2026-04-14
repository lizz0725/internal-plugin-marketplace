# 内部插件市场

企业内部 Claude Code 插件市场，支持插件提交、审核、评分和安装。

## 项目结构

```
internal-plugin-marketplace/
├── backend/           # FastAPI 后端
├── frontend/          # Vue 3 前端
├── plugins-repo/      # 插件仓库（Git 管理）
└── docs/              # 设计文档
```

## 快速启动

### 1. 启动后端

```bash
cd backend

# 创建虚拟环境（首次）
python3 -m venv venv

# 安装依赖（首次）
./venv/bin/pip install fastapi uvicorn pydantic

# 启动服务
./venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

后端地址: http://127.0.0.1:8000

### 2. 启动前端

```bash
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

前端地址: http://localhost:3000

## 配置

### 后端配置 (backend/.env)

```bash
# 插件仓库路径（相对于 backend 目录）
PLUGINS_REPO_PATH=../plugins-repo

# 远程 Git 仓库 URL（用于客户端安装）
PLUGINS_REPO_URL=https://github.com/your-org/your-marketplace.git

# 市场名称
MARKETPLACE_NAME=内部插件市场

# 管理员邮箱（逗号分隔）
ADMIN_EMAILS=admin@company.com
```

### 前端配置 (frontend/vite.config.js)

API 代理已配置为 `http://127.0.0.1:8000`

## 功能

### 用户功能
- 浏览插件列表
- 搜索插件
- 查看插件详情
- 评分评论
- 提交新插件

### 管理员功能
- 审核待提交插件
- 批准/拒绝插件
- 查看统计数据

### 审批流程
1. 用户提交插件 → 创建 pending 目录
2. 管理员审核 → 批准/拒绝
3. 批准后自动：
   - 创建插件目录
   - 生成版本标签
   - Git commit
   - **自动推送到远程仓库**

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/plugins/` | GET | 插件列表 |
| `/api/plugins/{name}` | GET | 插件详情 |
| `/api/plugins/submit` | POST | 提交插件 |
| `/api/plugins/{name}/rate` | POST | 评分 |
| `/api/reviews/pending` | GET | 待审核列表 |
| `/api/reviews/all` | GET | 所有提交 |
| `/api/reviews/{id}/approve` | POST | 批准 |
| `/api/reviews/{id}/reject` | POST | 拒绝 |
| `/api/stats/` | GET | 统计数据 |

## 客户端安装

用户可通过 Claude Code CLI 安装内部插件：

```bash
# 添加市场
claude plugin marketplace add https://github.com/your-org/your-marketplace.git

# 安装插件
claude plugin install plugin-name@your-marketplace-name

# 查看已安装
claude plugin list
```

## 插件仓库结构

```
plugins-repo/
├── .claude-plugin/
│   └── marketplace.json    # Claude Code 市场配置
├── plugins/
│   └── {plugin-name}/
│       └── .claude-plugin/
│           ├── plugin.json    # 插件元数据
│           └── versions.json  # 版本历史
├── ratings/
│   └── {plugin-name}.json    # 评分数据
├── pending/
│   └── submissions/           # 待审核提交
└── marketplace.json           # 市场元信息
```

## 开发

### 技术栈
- 后端: Python 3 + FastAPI + Pydantic
- 前端: Vue 3 + Vite + Pinia + Axios
- 数据存储: Git 仓库 + JSON 文件

### 主题设计
- 深色背景 (#1A1A1F)
- 琥珀金强调 (#D4A574)
- JetBrains Mono (代码)
- Crimson Pro (正文)

## 设计文档

- [系统设计文档](docs/specs/2026-04-13-internal-plugin-marketplace-design.md)
- [实现计划](docs/superpowers/plans/2026-04-13-implementation-plan.md)