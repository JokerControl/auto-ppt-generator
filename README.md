# AutoPPT Generator

智能 PPT 自动生成系统，基于 AI 技术帮助用户快速创建专业演示文稿。

## 🚀 功能特点

- 🤖 **AI 智能生成** - 输入主题自动生成 PPT 大纲和内容
- 🎨 **多种模板** - 支持多种风格模板（现代、商务、创意等）
- 📝 **实时编辑** - 支持大纲和内容的实时修改
- 📦 **一键导出** - 支持导出 PPTX、PDF 等格式
- 🔄 **API 支持** - 提供完整的 RESTful API

## 🛠 技术栈

- **后端**: Python 3.9+ / FastAPI
- **前端**: React 18 / TypeScript / Vite
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **AI 服务**: MiniMax API
- **部署**: Docker / Docker Compose

## 📋 环境要求

### 开发环境
- Python 3.9+
- Node.js 18+
- Git

### 生产环境（推荐）
- CPU: 2+ 核心
- 内存: 4GB+
- 存储: 20GB+

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/JokerControl/auto-ppt-generator.git
cd auto-ppt-generator

# 2. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 .env，填入你的 MiniMax API Key

# 3. 启动服务
cd docker
docker-compose up -d

# 4. 访问应用
# 前端: http://localhost:5173
# 后端 API: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 方式二：手动部署

#### 后端部署

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入必要配置

# 5. 启动服务
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端部署

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env

# 4. 启动开发服务器
npm run dev

# 5. 构建生产版本
npm run build
```

## ⚙️ 配置说明

### 后端环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `MINIMAX_API_KEY` | MiniMax API 密钥 | `your-api-key` |
| `MINIMAX_BASE_URL` | API 地址 | `https://api.minimax.com/v1` |
| `MINIMAX_MODEL` | 使用的模型 | `abab6.5s-chat` |
| `DEBUG` | 调试模式 | `true` |
| `HOST` | 服务地址 | `0.0.0.0` |
| `PORT` | 服务端口 | `8000` |

### 创建 .env 文件

```bash
# 后端目录
cd backend

# 复制示例配置
cp .env.example .env

# 编辑配置
nano .env
```

`.env.example` 内容：

```env
# MiniMax API 配置（必须）
MINIMAX_API_KEY=your_api_key_here
MINIMAX_BASE_URL=https://api.minimax.com/v1
MINIMAX_MODEL=abab6.5s-chat

# 应用配置
DEBUG=true
HOST=0.0.0.0
PORT=8000

# 存储配置
OUTPUT_DIR=./output
MAX_FILE_SIZE=52428800
```

## 📡 API 文档

启动后端服务后，访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ppt/generate` | 生成 PPT |
| GET | `/api/ppt/status/{task_id}` | 查询生成状态 |
| GET | `/api/ppt/download/{task_id}` | 下载 PPT 文件 |
| GET | `/api/ppt/list` | 获取生成记录 |

### API 使用示例

```bash
# 生成 PPT
curl -X POST http://localhost:8000/api/ppt/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "人工智能在教育中的应用",
    "page_count": 10,
    "style": "modern",
    "language": "zh-CN"
  }'

# 查询状态
curl http://localhost:8000/api/ppt/status/{task_id}

# 下载文件
curl -o output.pptx http://localhost:8000/api/ppt/download/{task_id}
```

## 🐳 Docker 部署详解

### docker-compose.yml 配置

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./output:/app/output
    environment:
      - MINIMAX_API_KEY=${MINIMAX_API_KEY}
      - DEBUG=false
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### Docker 命令

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps
```

## 🔧 故障排除

### 常见问题

#### 1. 依赖安装失败
```bash
# 清理缓存后重试
pip cache purge
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. 端口被占用
```bash
# 查看端口占用
lsof -i :8000

# 更改端口或停止占用进程
```

#### 3. API 调用失败
- 检查 `MINIMAX_API_KEY` 是否正确
- 检查网络连接
- 查看后端日志

#### 4. 文件权限问题
```bash
# Linux/Mac
chmod -R 755 ./output
```

## 📁 项目结构

```
auto-ppt-generator/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模型
│   │   └── services/       # 业务服务
│   ├── main.py             # 应用入口
│   ├── requirements.txt     # Python 依赖
│   └── .env.example        # 环境变量示例
│
├── frontend/               # React 前端
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── pages/          # 页面
│   │   ├── services/       # API 服务
│   │   └── utils/          # 工具函数
│   ├── package.json        # Node 依赖
│   └── vite.config.ts      # Vite 配置
│
├── docker/                 # Docker 配置
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
│
└── docs/                   # 项目文档
```

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 了解详情

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

---

Made with ❤️ by Joker
