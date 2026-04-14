---
title: 内部插件市场系统设计文档
date: 2026-04-13
status: approved
---

# 内部插件市场系统设计文档

## 项目概述

为企业内部团队构建一个 Claude Code 插件市场系统，提供插件分发、审核管理、版本控制、用户评分反馈等功能。

### 目标

- 提供统一的内部插件分发渠道
- 支持插件审核流程，确保质量与安全
- 版本管理，用户可安装指定版本
- 用户评分和反馈机制，促进插件改进

### 非目标

- 不实现复杂的权限控制（全员开放）
- 不修改 Claude Code 客户端核心代码

---

## 系统架构

### 方案选择

选择 **方案 A: Git 主导 + Web 覆盖层**：

- 插件和市场元数据存储在 Git 仓库中
- Web 管理后台读取 Git 仓库，提供浏览和管理界面
- Claude Code 客户端直接从 Git 仓库安装插件

### 架构图

```
┌─────────────────────────────────────────────┐
│  Vue 前端 + FastAPI 后端                     │
│  ├─ 插件浏览页面                             │
│  ├─ 审核管理页面                             │
│  ├─ 统计分析页面                             │
│  └─ Git 操作层                              │
└─────│───────────────────────────────────────┘
      ↓ Git Clone/Pull/Commit
┌─────────────────────────────────────────────┐
│  内部 Git 仓库                               │
│  ├─ marketplace.json                        │
│  ├─ plugins/                                │
│  ├─ pending/                                │
│  ├─ reviews/                                │
│  └─ ratings/                                │
└─────────────────────────────────────────────┘
      ↓ Git Clone
┌─────────────────────────────────────────────┐
│  Claude Code 客户端                          │
│  /plugin install nl2sql@internal             │
└─────────────────────────────────────────────┘
```

---

## Git 仓库结构

### 目录结构

```
internal-plugins-marketplace/
├── README.md                    # 市场介绍
├── marketplace.json             # 市场元数据
├── plugins/                     # 已上架插件
│   ├── nl2sql/
│   │   ├── .claude-plugin/
│   │   │   ├── plugin.json
│   │   │   └── versions.json
│   │   ├── skills/
│   │   └── README.md
│   └── ...
├── pending/                     # 待审核
│   ├── submissions/
│   │   └── {date}-{uuid}/
│   │       ├── plugin.json
│   │       ├── submitter.json
│   │       └── files/
│   └── reviews.json
├── reviews/                     # 审核历史
│   └── 2024-Q1.json
├── ratings/                     # 评分反馈
│   └── nl2sql.json
└── stats/                       # 统计数据
    └── install_counts.json
```

### 文件格式

#### marketplace.json

```json
{
  "name": "internal-plugins-marketplace",
  "display_name": "公司内部插件市场",
  "description": "企业内部 Claude Code 插件仓库",
  "owner": {
    "name": "技术基础设施团队",
    "email": "infra@company.com"
  },
  "repository": "https://gitlab.company.com/claude/plugins-marketplace",
  "created_at": "2024-01-01",
  "plugins_count": 15
}
```

#### plugin.json

```json
{
  "name": "nl2sql",
  "description": "自然语言转 SQL 查询技能",
  "version": "1.2.0",
  "author": {
    "name": "数据平台团队",
    "email": "data-platform@company.com"
  },
  "keywords": ["database", "sql", "nl2sql"],
  "license": "proprietary",
  "homepage": "https://gitlab.company.com/data-platform/nl2sql-plugin"
}
```

#### versions.json

```json
{
  "current": "1.2.0",
  "versions": [
    {
      "version": "1.2.0",
      "released_at": "2024-03-15",
      "git_ref": "nl2sql-v1.2.0",
      "changelog": "添加多表联合查询支持",
      "status": "current"
    },
    {
      "version": "1.1.0",
      "released_at": "2024-02-01",
      "git_ref": "nl2sql-v1.1.0",
      "changelog": "初始版本",
      "status": "available"
    }
  ]
}
```

#### ratings/{plugin}.json

```json
{
  "plugin": "nl2sql",
  "average_rating": 4.5,
  "total_ratings": 23,
  "ratings": [
    {
      "user": "zhang.san@company.com",
      "rating": 5,
      "comment": "非常好用，大大提升效率",
      "rated_at": "2024-03-20"
    }
  ]
}
```

---

## Web 管理后台

### 技术栈

- **后端**: Python + FastAPI
- **前端**: Vue 3 + Vite
- **部署**: 内网服务器 + Nginx
- **认证**: 公司 SSO 系统集成

### 角色定义

| 角色 | 定义方式 | 权限范围 |
|-----|---------|---------|
| 普通用户 | SSO 认证的内部员工 | 浏览插件、提交审核、评分反馈 |
| 管理员 | 配置文件 `admins.json` 或 SSO 组成员 | 审核插件、发布版本、查看统计 |

**admins.json** 格式：
```json
{
  "admins": [
    "li.si@company.com",
    "wang.wu@company.com"
  ]
}
```

### 页面设计

| 页面 | 路径 | 功能 | 权限 |
|-----|-----|------|-----|
| 插件浏览 | `/plugins` | 搜索、卡片展示、安装命令 | 全员 |
| 插件详情 | `/plugins/:name` | 版本历史、评分评论、安装 | 全员 |
| 插件提交 | `/submit` | 表单提交审核 | 全员 |
| 我的提交 | `/my-submissions` | 查看提交状态和历史 | 全员 |
| 审核管理 | `/admin/reviews` | 待审核列表、审核操作 | 管理员 |
| 统计分析 | `/admin/stats` | 安装趋势、评分分布 | 管理员 |

### API 设计

| 端点 | 方法 | 功能 | 权限 |
|-----|-----|------|-----|
| `/api/plugins` | GET | 插件列表 | 全员 |
| `/api/plugins/{name}` | GET | 插件详情 | 全员 |
| `/api/plugins/submit` | POST | 提交审核 | 全员 |
| `/api/plugins/{name}/rate` | POST | 用户评分 | 全员 |
| `/api/reviews/pending` | GET | 待审核列表 | 管理员 |
| `/api/reviews/{id}/approve` | POST | 审核通过 | 管理员 |
| `/api/reviews/{id}/reject` | POST | 审核拒绝 | 管理员 |
| `/api/stats/overview` | GET | 统计概览 | 管理员 |

### Git 操作层

**GitRepoReader**:
- `git clone --depth=1` 获取快照
- 解析 JSON 文件为 Python 对象
- 缓存解析结果

**GitRepoWriter**:
- 审核通过：移动文件、更新 versions.json、创建 tag
- 用户评分：追加写入 ratings/{plugin}.json
- 所有变更生成一个 commit

**GitSyncService**:
- 定时拉取（每 5 分钟）
- 更新本地缓存
- 处理并发冲突（乐观锁 + retry）

---

## 版本管理

### 版本标识

- Git Tag: `plugin-name-vX.Y.Z`
- 版本号: Semantic Versioning (MAJOR.MINOR.PATCH)

### 版本发布流程

```
开发者 → 提交审核 → pending/submissions/{id}/
                          ↓
管理员审核 → 通过 → 移动到 plugins/{name}/
                 → 更新 versions.json
                 → 创建 git tag
                 → 通知开发者
```

### 用户安装

```bash
# 最新版本
/plugin install nl2sql@internal

# 指定版本
/plugin install nl2sql@internal@1.1.0

# 指定 git ref
/plugin install nl2sql@internal@nl2sql-v1.1.0
```

### 版本状态

- `current`: 当前推荐版本
- `available`: 可安装的历史版本
- `deprecated`: 已废弃，安装时警告

---

## 审核流程

### 流程图

```
提交者 → 填写表单 → pending/submissions/{uuid}/
                            ↓
管理员 → 查看内容 → 自动检查（可选）
                 → 决定：通过 / 拒绝
                            ↓
            ┌───────────────┴───────────────┐
            ↓                               ↓
        通过审核                          拒绝审核
            ↓                               ↓
    移动到 plugins/{name}/           记录拒绝原因
    创建 git tag                     通知提交者
    通知提交者
```

### 提交信息

**submitter.json**:
```json
{
  "name": "张三",
  "email": "zhang.san@company.com",
  "department": "数据平台团队",
  "submitted_at": "2024-03-15T10:30:00Z",
  "message": "这是 NL2SQL 技能插件..."
}
```

**review_status.json**:
```json
{
  "submission_id": "2024-03-15-001",
  "status": "approved",
  "reviewed_by": "li.si@company.com",
  "reviewed_at": "2024-03-16T14:00:00Z",
  "review_notes": "插件结构规范，功能测试通过"
}
```

### 自动化检查

审核流程中包含以下自动化检查项：

| 检查项 | 说明 | 结果处理 |
|-----|------|---------|
| 结构验证 | 检查 `.claude-plugin/plugin.json` 存在且格式正确 | 失败则阻止提交 |
| 安全扫描 | 检查是否有 `.env`, `credentials`, `secrets` 等敏感文件 | 失败则警告管理员 |
| 依赖检查 | 验证 `.mcp.json` 中引用的 MCP 服务可达 | 失败则警告管理员 |

检查结果展示在审核页面供管理员参考。

### 通知机制

审核结果通过以下方式通知提交者：

- **邮件通知**: 使用公司邮件系统发送审核结果
- **Web 界面**: 提交者可在 `/my-submissions` 页面查看提交状态
- **API 回调** (可选): 支持配置 webhook URL 推送审核结果

---

## 用户评分系统

### 评分规则

- 评分范围：1-5 星
- 每用户每插件限一次评分
- 用户可编辑/删除自己的评分

### API

```
POST /api/plugins/{name}/rate
{
  "rating": 5,
  "comment": "非常好用",
  "user_email": "zhang.san@company.com"
}
```

### 展示

- 卡片：平均评分（星级图标）
- 详情页：评论列表
- 管理后台：评分分布图表

---

## 部署架构

### 架构图

```
企业内网
├── GitLab/GitHub Enterprise (git.company.com)
│   └── 插件仓库
│
├── 插件市场服务 (plugins.company.com)
│   ├── FastAPI 后端
│   ├── Vue 前端
│   ├── Nginx 反向代理
│   └── Redis 缓存（可选）
│
└── 用户电脑
    └── Claude Code CLI
        ├── /plugin add-marketplace internal git.company.com/team/plugins-marketplace
        └── /plugin install nl2sql@internal
```

### 用户配置

```bash
/plugin add-marketplace internal git.company.com/team/plugins-marketplace
```

### 安全措施

| 项目 | 方案 |
|-----|-----|
| Git 访问 | 仓库 Internal/Private，用户 SSH Key/SSO |
| 后台认证 | 公司 SSO/OAuth |
| 插件扫描 | 提交时自动检查敏感文件 |
| 数据隔离 | 用户邮箱匿名化展示 |

### 运维建议

- 高可用：多实例 + Nginx 负载均衡
- 监控：健康检查、Git 同步告警、审核队列告警
- 备份：Git 仓库是备份源，定期 clone 到异地

---

## 项目范围

### 第一阶段（核心功能）

1. Git 仓库结构搭建
2. 基础插件浏览页面
3. 插件提交审核流程
4. 用户评分功能

### 第二阶段（增强功能）

1. 版本管理页面
2. 统计分析页面
3. 自动化检查集成
4. 变更日志展示

### 第三阶段（可选扩展）

1. 插件依赖关系图
2. 推荐算法
3. 批量安装脚本
4. 移动端适配

---

## 开发计划

待实现计划另行编写。