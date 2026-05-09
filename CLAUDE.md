# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

上游聚合市场 - 从 GitHub 热门仓库拉取 Claude Code 插件和 skill，聚合到一个 Git 仓库中，支持双远程推送（GitHub + Gitee）。最终用户通过 `/plugin marketplace add <url>` 添加市场后直接 `/plugin install <name>` 安装。

## Commands

### Backend (FastAPI)
```bash
cd backend
./venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

### Frontend (Vue 3 + Vite)
```bash
cd frontend
npm run dev          # 开发服务器 (localhost:3000)
npm run build        # 生产构建
```

### Sync Script
```bash
python3 scripts/sync_plugins.py              # 同步所有 pending 插件
python3 scripts/sync_plugins.py --all        # 强制全量同步
python3 scripts/sync_plugins.py --status     # 仅查看状态
python3 scripts/sync_plugins.py --name foo   # 同步单个插件
python3 scripts/sync_plugins.py --no-push    # 仅本地更新，不推送
```

## Architecture

### 三层结构
- **backend/**: FastAPI REST API，提供插件浏览、评分、同步状态接口
- **frontend/**: Vue 3 SPA，插件浏览/详情/同步管理界面
- **plugins-repo/**: Git 仓库，JSON 文件存储所有插件数据和来源追踪信息

### 数据流
```
上游 GitHub 仓库 → scripts/sync_plugins.py → plugins-repo/plugins/{name}/
                                            → sources.json (来源追踪)
                                            → .claude-plugin/marketplace.json (自动生成)
                                            → git push GitHub + Gitee
                                            → 客户端 /plugin marketplace add <url>
                                            → /plugin install <name>
```

### Backend 核心模块
- `app/git_ops.py`: GitRepoReader/GitRepoWriter - 所有数据读写通过此模块
- `app/models.py`: Pydantic 数据模型（PluginWithSource, SourceInfo 等）
- `app/routers/plugins.py`: 插件浏览列表/详情/评分 API
- `app/routers/stats.py`: 统计概览/评分分布 API
- `app/main.py`: FastAPI 入口，额外注册 `/api/sync/status` 和 `/api/sync/trigger`

### Frontend 核心结构
- `src/api/index.js`: Axios API 客户端
- `src/views/`: 4 个页面组件（PluginsList, PluginDetail, AdminSync, AdminStats）
- `src/router/index.js`: Vue Router 配置

### 插件仓库结构
```
plugins-repo/
├── .claude-plugin/marketplace.json  # Claude Code 市场配置（自动生成）
├── sources.json                     # 来源注册中心（repo URL、commit SHA、同步状态）
├── plugins/{name}/.claude-plugin/   # 已同步插件（同名目录放 source.json）
├── plugins/{name}/source.json       # 单插件来源信息
├── ratings/{name}.json              # 评分数据
```

## Key Patterns

### JSON 序列化
写入 JSON 时使用 `model_dump(exclude_none=True)` 避免 `homepage: null` 导致 Claude Code 校验失败。

### 前端主题
深色背景 (#1A1A1F) + 琥珀金强调 (#D4A574)，CSS 变量在 `frontend/src/styles/variables.css`。

## Configuration

后端配置在 `backend/.env`:
- `PLUGINS_REPO_PATH`: 本地插件仓库路径（默认 `../plugins-repo`）
- `PLUGINS_REPO_URL`: Git 远程地址（客户端安装用）
- `ADMIN_EMAILS`: 管理员邮箱（逗号分隔）
