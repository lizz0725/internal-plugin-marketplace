# 开发指南

## 启动后端 (FastAPI)

```bash
cd backend
./venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

API 文档: http://localhost:8000/docs

## 启动前端 (Vue 3 + Vite)

```bash
cd frontend
npm run dev
```

访问: http://localhost:3000

## 生产构建

```bash
cd frontend
npm run build        # 输出到 dist/
```
