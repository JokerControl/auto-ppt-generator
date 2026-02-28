# AutoPPT Generator - 技术架构设计

## 1. 系统架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           用户访问层                                     │
│                    (Web浏览器 / 移动端)                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           CDN + 静态资源                                │
│                    (Cloudflare - 免费CDN)                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         前端服务 (Frontend)                             │
│              React + TypeScript + TailwindCSS                           │
│              托管: Vercel/Netlify (免费)                                │
│              端口: 80/443                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                              HTTPS/WSS
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API网关 (API Gateway)                           │
│                    Nginx (反向代理 + 负载均衡)                           │
│                    端口: 8000                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       后端服务 (Backend)                                │
│              FastAPI + Python 3.11                                      │
│              端口: 8001                                                 │
│              托管: Railway/Render (免费)                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│   MCP Server      │   │   PPT Generator   │   │   File Manager    │
│   (MCP Skills)    │   │   (python-pptx)   │   │   (Storage)       │
│   端口: 8002      │   │                   │   │                   │
└───────────────────┘   └───────────────────┘   └───────────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        MiniMax API (付费)                               │
│              https://api.minimax.chat/v1                               │
│              用户需自行申请API Key                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         数据存储层                                       │
│    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐               │
│    │   SQLite    │    │  本地文件   │    │  临时文件   │               │
│    │  (免费)     │    │  存储       │    │  缓存       │               │
│    └─────────────┘    └─────────────┘    └─────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2. 技术栈选型 (免费成本)

| 层级 | 技术选型 | 成本 | 说明 |
|------|----------|------|------|
| 前端框架 | React 18 + TypeScript | 免费 | 现代化前端框架 |
| UI组件 | TailwindCSS + HeadlessUI | 免费 | 原子化CSS |
| 前端构建 | Vite | 免费 | 快速构建工具 |
| 前端托管 | Vercel | 免费 | 每月100GB流量 |
| 后端框架 | FastAPI | 免费 | 高性能Python框架 |
| 后端托管 | Railway/Render | 免费 | 每月$5免费额度 |
| PPT生成 | python-pptx | 免费 | Python PPT库 |
| 数据库 | SQLite | 免费 | 嵌入式数据库 |
| 文件存储 | 本地文件系统 | 免费 | 容器内存储 |
| CDN | Cloudflare | 免费 | 安全+加速 |
| 容器化 | Docker + Docker Compose | 免费 | |

## 3. MiniMax API 集成方案

### 3.1 API 配置

```python
# 环境变量配置
MINIMAX_API_KEY=your_api_key_here
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=abab6.5s-chat
```

### 3.2 API 调用流程

```python
# PPT生成请求流程
1. 用户输入主题 → 2. 后端接收请求 → 3. 调用MiniMax API 
→ 4. 获取生成内容 → 5. MCP处理优化 → 6. python-pptx生成文件
→ 7. 返回下载链接
```

### 3.3 API 代理服务设计

```python
# 后端 API 端点
POST /api/v1/ppt/generate     # 生成PPT
GET  /api/v1/ppt/status/{id}  # 查询状态
GET  /api/v1/ppt/download/{id} # 下载文件
POST /api/v1/ppt/preview      # 预览大纲
```

## 4. MCP 技能实现方案

### 4.1 MCP Server 架构

```
┌─────────────────────────────────────────┐
│           MCP Protocol Layer            │
│    (JSON-RPC 2.0 over stdio/HTTP)       │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ ppt.     │  │ ppt.     │  │ ppt.     │
│ analyze  │  │ generate │  │ export   │
└──────────┘  └──────────┘  └──────────┘
```

### 4.2 MCP 技能定义

```json
{
  "skills": [
    {
      "name": "ppt.analyze",
      "description": "分析PPT主题，提取关键信息",
      "parameters": {
        "type": "object",
        "properties": {
          "topic": {"type": "string"},
          "requirements": {"type": "string"}
        }
      }
    },
    {
      "name": "ppt.structure",
      "description": "生成PPT结构和大纲",
      "parameters": {
        "type": "object", 
        "properties": {
          "topic": {"type": "string"},
          "page_count": {"type": "integer"}
        }
      }
    },
    {
      "name": "ppt.content",
      "description": "填充PPT详细内容",
      "parameters": {
        "type": "object",
        "properties": {
          "outline": {"type": "object"},
          "style": {"type": "string"}
        }
      }
    },
    {
      "name": "ppt.design",
      "description": "应用设计模板和样式",
      "parameters": {
        "type": "object",
        "properties": {
          "template": {"type": "string"},
          "theme": {"type": "string"}
        }
      }
    },
    {
      "name": "ppt.export",
      "description": "导出PPT为不同格式",
      "parameters": {
        "type": "object",
        "properties": {
          "format": {"type": "string", "enum": ["pptx", "pdf", "png"]},
          "quality": {"type": "string"}
        }
      }
    }
  ]
}
```

### 4.3 MCP 实现代码结构

```
mcp-server/
├── __init__.py
├── server.py           # MCP服务器主入口
├── protocol.py         # JSON-RPC协议处理
├── skills/
│   ├── __init__.py
│   ├── analyze.py      # ppt.analyze 技能
│   ├── structure.py    # ppt.structure 技能
│   ├── content.py      # ppt.content 技能
│   ├── design.py       # ppt.design 技能
│   └── export.py       # ppt.export 技能
└── tools/
    └── ppt_generator.py # PPT生成工具
```

## 5. Docker 容器化方案

### 5.1 Docker Compose 编排

```yaml
version: '3.8'

services:
  # 反向代理 + Web服务器
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    networks:
      - autoppt-network

  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=production
      - VITE_API_BASE_URL=http://nginx/api
    networks:
      - autoppt-network

  # 后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - MINIMAX_API_KEY=${MINIMAX_API_KEY}
      - DATABASE_URL=sqlite:///./data/autoppt.db
      - STORAGE_PATH=/app/storage
    volumes:
      - ppt-storage:/app/storage
      - ./data:/app/data
    depends_on:
      - mcp-server
    networks:
      - autoppt-network

  # MCP服务器
  mcp-server:
    build:
      context: ./mcp-server
      dockerfile: Dockerfile
    environment:
      - MCP_HOST=mcp-server
      - MCP_PORT=8002
    networks:
      - autoppt-network

volumes:
  ppt-storage:

networks:
  autoppt-network:
    driver: bridge
```

### 5.2 多阶段构建优化

```dockerfile
# 前端 Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```dockerfile
# 后端 Dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
RUN mkdir -p /app/storage /app/data
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 6. API 接口设计

### 6.1 接口列表

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | /api/v1/ppt/generate | 生成PPT | API Key |
| GET | /api/v1/ppt/status/{task_id} | 查询生成状态 | API Key |
| GET | /api/v1/ppt/download/{task_id} | 下载PPT文件 | API Key |
| POST | /api/v1/ppt/preview | 预览PPT大纲 | API Key |
| DELETE | /api/v1/ppt/{task_id} | 删除PPT | API Key |
| GET | /api/v1/ppt/list | 获取PPT列表 | API Key |
| GET | /health | 健康检查 | 无 |

### 6.2 请求/响应示例

```json
// POST /api/v1/ppt/generate
// Request
{
  "topic": "人工智能在教育中的应用",
  "page_count": 10,
  "style": "modern",
  "language": "zh-CN",
  "template": "default"
}

// Response
{
  "task_id": "ppt_20240101_123456",
  "status": "processing",
  "message": "PPT生成中，请稍候...",
  "created_at": "2024-01-01T12:00:00Z"
}
```

## 7. 数据模型设计

### 7.1 SQLite 数据库表

```sql
-- 用户表 (可选，用于后续扩展)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PPT生成任务表
CREATE TABLE ppt_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    user_id INTEGER,
    topic TEXT NOT NULL,
    page_count INTEGER DEFAULT 10,
    style TEXT DEFAULT 'modern',
    status TEXT DEFAULT 'pending',
    file_path TEXT,
    file_size INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- PPT页面内容表
CREATE TABLE ppt_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    title TEXT,
    content TEXT,
    bullets TEXT,
    FOREIGN KEY (task_id) REFERENCES ppt_tasks(task_id)
);
```

## 8. 安全考虑

1. **API Key 认证**：所有API调用需要携带API Key
2. **CORS配置**：限制允许的域名
3. **请求限流**：防止API滥用
4. **文件安全**：限制文件上传类型和大小
5. **环境变量**：敏感信息通过环境变量配置，不硬编码

## 9. 部署架构 (生产环境)

```
                                    Internet
                                        │
                                        ▼
                                ┌───────────────┐
                                │  Cloudflare   │
                                │  (CDN + WAF)  │
                                └───────────────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │  Docker Host  │
                                │  (1核1G)      │
                                └───────────────┘
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            │                           │                           │
            ▼                           ▼                           ▼
    ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
    │    Nginx      │          │   Backend     │          │  MCP Server   │
    │  (Reverse     │◄─────────►│  (FastAPI)    │◄────────►│  (Python)     │
    │   Proxy)      │          │               │          │               │
    └───────────────┘          └───────────────┘          └───────────────┘
            │                           │                           │
            ▼                           ▼                           │
    ┌───────────────┐          ┌───────────────┐                   │
    │   Frontend    │          │    SQLite     │◄──────────────────┘
    │   (Static)    │          │   + Files     │
    └───────────────┘          └───────────────┘
```

## 10. 免费部署指南

1. **Vercel**: 连接GitHub仓库，自动部署前端
2. **Railway**: 连接GitHub仓库，自动部署后端
3. **Cloudflare**: 配置DNS和CDN
4. **MiniMax**: 申请API Key并配置环境变量

预计月成本: **0元** (仅MiniMax API调用付费)
