# 快速启动指南

## 一键启动（推荐）

```bash
# 在 backend 目录下运行
cd /home/user/shangjiwebsite/backend
./scripts/setup.sh
```

这个脚本会自动：
1. 启动 Docker 服务（PostgreSQL, Redis, MinIO）
2. 初始化数据库表结构
3. 创建测试用户账号

## 测试账号

所有账号的密码都是：`password123`

| 用户名 | 角色 | 说明 |
|--------|------|------|
| `admin` | 管理员 | 完整系统权限 |
| `ocr_editor` | OCR编辑员 | 编辑OCR内容 |
| `ocr_reviewer` | OCR审核员 | 审核OCR内容 |
| `rewrite_editor` | 改写编辑员 | 编辑改写内容 |
| `rewrite_reviewer` | 改写审核员 | 审核改写内容 |

## 启动服务

### 1. 启动后端 API

```bash
# 终端1: FastAPI 服务器
python -m app.main

# 或使用 uvicorn（支持热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

访问 API 文档：http://localhost:8080/docs

### 2. 启动 Celery Worker

```bash
# 终端2: Celery 异步任务处理器（处理OCR任务）
celery -A app.core.celery_app worker --loglevel=info
```

### 3. 启动前端

```bash
# 终端3
cd ../frontend

# 如果没有 .env 文件，创建一个
cp .env.example .env

# 启动开发服务器
npm run dev
```

访问前端：http://localhost:3000

## 完整测试流程

1. **登录** - 使用 `admin` / `password123`
2. **创建题目** - 上传图片，自动触发OCR
3. **OCR编辑** - 用 `ocr_editor` 账号登录，编辑OCR结果
4. **OCR审核** - 用 `ocr_reviewer` 账号登录，审核通过
5. **改写编辑** - 用 `rewrite_editor` 账号登录，编辑5个版本
6. **改写审核** - 用 `rewrite_reviewer` 账号登录，审核5个版本
7. **完成** - 题目状态变为 DONE

## 手动初始化（可选）

如果不想用一键脚本，可以手动执行：

```bash
# 1. 启动 Docker 服务
docker-compose up -d

# 2. 等待 PostgreSQL 启动
sleep 5

# 3. 初始化数据库
python scripts/init_db.py

# 4. 创建用户
python scripts/create_initial_users.py
```

## 常见问题

### 端口被占用？
- FastAPI: 默认8080端口
- Frontend: 默认3000端口
- PostgreSQL: 默认5432端口
- Redis: 默认6379端口

修改配置文件中的端口即可。

### 数据库连接失败？
检查 Docker 服务是否启动：
```bash
docker-compose ps
```

### MinIO 访问失败？
MinIO 控制台：http://localhost:9001
- 用户名：minioadmin
- 密码：minioadmin

## 停止服务

```bash
# 停止 Docker 服务
docker-compose down

# 如果要删除数据（慎用）
docker-compose down -v
```
