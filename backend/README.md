# 熵基秩序 - 后端服务

基于 FastAPI 的后端 API 服务。

## 功能特性

- 用户认证（注册/登录）
- JWT Token 认证
- PostgreSQL 数据库
- Docker 容器化部署

## 技术栈

- **框架**: FastAPI 0.109
- **数据库**: PostgreSQL + SQLAlchemy 2.0
- **认证**: JWT + Bcrypt
- **容器化**: Docker + Docker Compose

## 快速开始

### 1. 环境要求

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和密钥
```

### 4. 启动服务

#### 使用 Docker Compose（推荐）

```bash
docker-compose up -d
```

#### 手动启动

```bash
# 启动数据库
docker-compose up -d postgres

# 启动后端
python -m app.main
```

### 5. 访问 API 文档

- Swagger UI: http://localhost:8080/api/docs
- ReDoc: http://localhost:8080/api/redoc

## API 端点

### 认证

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录

### 健康检查

- `GET /health` - 服务健康状态

## 开发说明

### 项目结构

```
backend/
├── app/
│   ├── api/v1/         # API 路由
│   ├── core/           # 核心配置
│   ├── models/         # 数据库模型
│   ├── schemas/        # Pydantic schemas
│   └── main.py         # 主应用入口
├── Dockerfile          # Docker 镜像配置
├── docker-compose.yml  # Docker Compose 配置
└── requirements.txt    # Python 依赖
```

## 作者

HongdiHe

## 许可证

MIT
