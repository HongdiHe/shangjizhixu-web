# Shangji Question Processing System - Backend

基于 FastAPI 的题目处理系统后端服务。

## 技术栈

- **FastAPI + Uvicorn**: 异步 Web 框架
- **SQLAlchemy 2.0 + Alembic**: ORM 和数据库迁移
- **Celery + Redis**: 异步任务队列
- **PostgreSQL**: 主数据库
- **Redis**: 缓存和消息队列
- **MinIO**: 对象存储
- **Pydantic**: 数据验证

## 项目结构

```
backend/
├── app/
│   ├── api/            # API 路由
│   │   └── v1/
│   │       ├── auth.py        # 认证接口
│   │       ├── users.py       # 用户管理接口
│   │       └── questions.py   # 题目管理接口
│   ├── core/           # 核心配置
│   │   ├── config.py          # 应用配置
│   │   ├── database.py        # 数据库配置
│   │   ├── security.py        # 安全工具
│   │   ├── dependencies.py    # 依赖注入
│   │   └── celery_app.py      # Celery 配置
│   ├── models/         # 数据库模型
│   │   ├── enums.py           # 枚举类型
│   │   ├── user.py            # 用户模型
│   │   └── question.py        # 题目模型
│   ├── schemas/        # Pydantic schemas
│   │   ├── common.py          # 公共 schema
│   │   ├── user.py            # 用户 schema
│   │   └── question.py        # 题目 schema
│   ├── services/       # 业务逻辑
│   │   ├── user_service.py       # 用户服务
│   │   ├── question_service.py   # 题目服务
│   │   └── storage_service.py    # 存储服务
│   ├── tasks/          # Celery 任务
│   │   ├── ocr_tasks.py       # OCR 处理任务
│   │   └── llm_tasks.py       # LLM 改写任务
│   ├── utils/          # 工具函数
│   │   └── markdown_converter.py  # Markdown 转换
│   └── main.py         # 应用入口
├── alembic/            # 数据库迁移
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/              # 测试
├── docker-compose.yml  # Docker Compose 配置
├── Dockerfile          # Docker 镜像
├── requirements.txt    # Python 依赖
├── pyproject.toml      # 项目配置
├── alembic.ini         # Alembic 配置
└── .env.example        # 环境变量示例
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd backend

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置数据库、Redis、MinIO 等
```

### 3. 使用 Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

服务访问地址：
- **Backend API**: http://localhost:8080
- **API 文档**: http://localhost:8080/api/docs
- **Flower (Celery 监控)**: http://localhost:5555
- **MinIO Console**: http://localhost:9001

### 4. 手动启动（开发模式）

#### 启动 PostgreSQL、Redis、MinIO

```bash
# 使用 Docker 启动基础服务
docker-compose up -d postgres redis minio
```

#### 运行数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

#### 启动 FastAPI 服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

#### 启动 Celery Worker

```bash
celery -A app.core.celery_app worker --loglevel=info --concurrency=4
```

#### 启动 Celery Beat（可选）

```bash
celery -A app.core.celery_app beat --loglevel=info
```

#### 启动 Flower（可选）

```bash
celery -A app.core.celery_app flower --port=5555
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8080/api/docs
- ReDoc: http://localhost:8080/api/redoc

## 核心功能

### 1. 用户认证与授权

- JWT Token 认证
- 基于角色的权限控制（RBAC）
- 角色类型：
  - Admin（管理员）
  - OCR Editor（OCR 编辑员）
  - OCR Reviewer（OCR 审查员）
  - Rewrite Editor（改写编辑）
  - Rewrite Reviewer（改写审查）

### 2. 题目处理流程

```
创建题目 → OCR处理(MinerU) → OCR编辑 → OCR审查
→ LLM改写(5次) → 改写编辑 → 改写审查 → 完成
```

### 3. Markdown 转换

- 自动将 Markdown 格式转换为单行要求格式
- 保护 LaTeX 公式不被破坏
- 在提交编辑和审查时自动执行

### 4. 异步任务

- **OCR 任务**: 调用 MinerU API 处理图片
- **LLM 任务**: 调用大模型 API 生成 5 个改写版本
- 任务状态可通过 Flower 监控

## 数据库管理

### 创建新迁移

```bash
alembic revision --autogenerate -m "描述"
```

### 执行迁移

```bash
alembic upgrade head
```

### 回滚迁移

```bash
alembic downgrade -1
```

### 查看迁移历史

```bash
alembic history
```

## 开发

### 代码格式化

```bash
black app/
```

### 类型检查

```bash
mypy app/
```

### 运行测试

```bash
pytest
```

### 代码覆盖率

```bash
pytest --cov=app --cov-report=html
```

## 配置说明

### 必需配置

- `DATABASE_URI`: PostgreSQL 数据库连接字符串
- `REDIS_URI`: Redis 连接字符串
- `SECRET_KEY`: JWT 签名密钥（生产环境必须使用强随机字符串）

### 可选配置

- `MINERU_API_URL` 和 `MINERU_API_KEY`: MinerU OCR 服务
- `LLM_API_URL` 和 `LLM_API_KEY`: 大模型服务
- `SENTRY_DSN`: Sentry 错误追踪

## 生产部署

### 1. 环境变量

- 修改 `SECRET_KEY` 为强随机字符串
- 设置 `ENVIRONMENT=production`
- 配置 CORS 允许的域名
- 配置生产数据库和 Redis

### 2. 反向代理

建议使用 Nginx 作为反向代理：

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 进程管理

使用 systemd 或 supervisor 管理进程。

### 4. 监控

- 使用 Prometheus + Grafana 监控指标
- 使用 Sentry 追踪错误
- 使用 Flower 监控 Celery 任务

## 故障排查

### 数据库连接失败

- 检查 PostgreSQL 是否运行
- 检查 `DATABASE_URI` 配置
- 检查网络连接

### Celery 任务不执行

- 检查 Redis 是否运行
- 检查 Celery Worker 是否启动
- 查看 Flower 监控面板

### MinIO 连接失败

- 检查 MinIO 是否运行
- 检查 `MINIO_ENDPOINT` 配置
- 检查存储桶是否创建

## 许可证

[Your License]

## 联系方式

[Your Contact Information]
