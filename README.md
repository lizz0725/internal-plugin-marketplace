# Internal Plugin Marketplace

企业内部 Claude Code 插件市场系统。

## 项目结构

```
internal-plugin-marketplace/
├── backend/          # FastAPI 后端
├── frontend/         # Vue 前端 (待实现)
├── plugins-repo/     # Git 插件仓库
└── docs/             # 设计文档和计划
```

## 快速开始

### 后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 插件仓库

```bash
cd plugins-repo
git init
```

## API 端点

| 端点 | 方法 | 功能 |
|-----|-----|------|
| `/api/plugins` | GET | 插件列表 |
| `/api/plugins/{name}` | GET | 插件详情 |
| `/api/plugins/submit` | POST | 提交审核 |
| `/api/plugins/{name}/rate` | POST | 用户评分 |
| `/api/reviews/pending` | GET | 待审核列表 |
| `/api/reviews/{id}/approve` | POST | 审核通过 |
| `/api/reviews/{id}/reject` | POST | 审核拒绝 |
| `/api/stats/overview` | GET | 统计概览 |

## 测试

```bash
cd backend
pytest tests/ -v
```

## 设计文档

- [系统设计文档](docs/specs/2026-04-13-internal-plugin-marketplace-design.md)
- [实现计划](docs/superpowers/plans/2026-04-13-implementation-plan.md)