# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

内部插件市场 - 企业内部 Claude Code 插件分享平台。用户可提交插件、管理员审核、审批后自动推送到 GitHub 供客户端安装。

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

## Architecture

### 三层结构
- **backend/**: FastAPI REST API，处理插件提交、审核、评分
- **frontend/**: Vue 3 SPA，插件浏览/提交/审核界面
- **plugins-repo/**: Git 仓库，JSON 文件存储所有数据

### 数据流
```
用户提交 → backend API → plugins-repo/pending/
管理员审批 → backend API → plugins-repo/plugins/ + Git commit + auto push
客户端安装 → claude plugin install → GitHub clone → 本地启用
```

### Backend 核心模块
- `app/git_ops.py`: GitRepoReader/GitRepoWriter - 所有数据读写通过此模块
- `app/models.py`: Pydantic 数据模型
- `app/routers/`: plugins, reviews, stats 三个 API 路由

### Frontend 核心结构
- `src/api/index.js`: Axios API 客户端，所有后端调用
- `src/views/`: 6 个页面组件（PluginsList, PluginDetail, SubmitPlugin, MySubmissions, AdminReviews, AdminStats）
- `src/router/index.js`: Vue Router 配置

### 插件仓库结构
```
plugins-repo/
├── .claude-plugin/marketplace.json  # Claude Code 市场配置（必需）
├── plugins/{name}/.claude-plugin/   # 已上架插件
├── pending/submissions/{id}/        # 待审核提交
├── ratings/{name}.json              # 评分数据
```

## Key Patterns

### Git 自动推送
审批通过后自动：创建插件目录 → 生成版本标签 → Git commit → `git push origin master --tags`

### JSON 序列化
写入 JSON 时使用 `model_dump(exclude_none=True)` 避免 `homepage: null` 导致 Claude Code 校验失败。

### 前端主题
深色背景 (#1A1A1F) + 琥珀金强调 (#D4A574)，CSS 变量在 `frontend/src/styles/variables.css`。

## Configuration

后端配置在 `backend/.env`:
- `PLUGINS_REPO_PATH`: 本地插件仓库路径
- `PLUGINS_REPO_URL`: GitHub 远程地址（客户端安装用）
- `ADMIN_EMAILS`: 管理员邮箱（逗号分隔）