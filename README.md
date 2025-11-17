# 熵基秩序题目管理系统

一个基于 FastAPI 和 React 的智能题目管理平台，支持试题的 OCR 识别、编辑改写、审核发布等完整工作流。

## 项目概述

本系统旨在提供一个完整的试题数字化处理并生成派生题目的解决方案，从原始图片的 OCR 识别，到人工校对编辑，再到 LLM 智能改写和多级审核，最终形成高质量的试题库。

### 核心功能

- **试题 OCR 识别**：支持上传试题图片，通过 OCR 技术自动识别题目和答案
- **分阶段编辑**：OCR 编辑和改写编辑分离，支持 Markdown 格式，实时预览
- **智能改写**：集成 LLM 能力，智能改写试题内容，支持手动触发
- **多级审核**：OCR 审核和改写审核两个独立环节，确保试题质量
- **精细化角色管理**：6 种角色（管理员、题目录入员、OCR编辑员、OCR审核员、改写编辑员、改写审核员）各司其职
- **任务管理**：个人任务面板，根据角色显示待处理的试题
- **系统配置**：灵活的系统参数配置（LLM 提示词、OCR 设置等）
- **完整工作流**：从图片上传到最终发布，全流程可追溯

### 技术栈

#### 后端
- **框架**：FastAPI + Uvicorn
- **数据库**：PostgreSQL + SQLAlchemy 2.0
- **任务队列**：Celery + Redis
- **对象存储**：MinIO / S3
- **OCR**：MinerU（可扩展）
- **LLM**：支持自定义 API 接入

#### 前端
- **框架**：React 18 + TypeScript
- **UI 库**：Ant Design 5
- **状态管理**：Zustand
- **数据获取**：TanStack Query (React Query)
- **路由**：React Router 6
- **编辑器**：Monaco Editor + React Markdown
- **构建工具**：Vite

## 项目结构

```
shangjizhixu-web/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   └── v1/           # API v1 版本
│   │   │       ├── auth.py   # 认证相关
│   │   │       ├── questions.py  # 试题相关
│   │   │       ├── upload.py     # 文件上传
│   │   │       ├── users.py      # 用户管理
│   │   │       └── system_config.py  # 系统配置
│   │   ├── core/              # 核心模块
│   │   │   ├── config.py     # 配置管理
│   │   │   ├── database.py   # 数据库连接
│   │   │   ├── security.py   # 安全认证
│   │   │   ├── dependencies.py  # 依赖注入
│   │   │   └── celery_app.py    # Celery 配置
│   │   ├── models/            # 数据模型
│   │   │   ├── user.py       # 用户模型
│   │   │   ├── question.py   # 试题模型
│   │   │   ├── system_config.py  # 系统配置模型
│   │   │   └── enums.py      # 枚举类型
│   │   ├── schemas/           # Pydantic 模式
│   │   ├── services/          # 业务逻辑
│   │   │   ├── user_service.py
│   │   │   ├── question_service.py
│   │   │   ├── storage_service.py
│   │   │   └── system_config_service.py
│   │   ├── tasks/             # Celery 异步任务
│   │   │   ├── ocr_tasks.py  # OCR 处理任务
│   │   │   └── llm_tasks.py  # LLM 改写任务
│   │   └── utils/             # 工具函数
│   ├── alembic/               # 数据库迁移
│   ├── scripts/               # 脚本工具
│   ├── tests/                 # 测试文件
│   ├── .env.example           # 环境变量示例
│   ├── requirements.txt       # Python 依赖
│   ├── docker-compose.yml     # Docker 编排
│   └── Dockerfile             # Docker 镜像
│
└── frontend/                   # 前端应用
    ├── src/
    │   ├── components/        # React 组件
    │   │   ├── layout/       # 布局组件
    │   │   └── upload/       # 上传组件
    │   ├── pages/             # 页面组件
    │   │   ├── LoginPage.tsx
    │   │   ├── DashboardPage.tsx
    │   │   ├── QuestionListPage.tsx
    │   │   ├── QuestionNewPage.tsx
    │   │   ├── QuestionDetailPage.tsx
    │   │   ├── QuestionOCREditPage.tsx
    │   │   ├── QuestionOCRReviewPage.tsx
    │   │   ├── QuestionRewriteEditPage.tsx
    │   │   ├── QuestionRewriteReviewPage.tsx
    │   │   ├── MyTasksPage.tsx
    │   │   └── SystemConfigPage.tsx
    │   ├── services/          # API 服务
    │   ├── store/             # 状态管理
    │   ├── hooks/             # 自定义 Hooks
    │   ├── types/             # TypeScript 类型
    │   ├── routes/            # 路由配置
    │   └── config/            # 配置文件
    ├── public/                # 静态资源
    ├── package.json           # 前端依赖
    ├── vite.config.ts         # Vite 配置
    └── tsconfig.json          # TypeScript 配置
```

## 快速开始

### 环境要求

- **Node.js**: >= 18.0.0
- **Python**: >= 3.11
- **PostgreSQL**: >= 14
- **Redis**: >= 6.0
- **Docker**: >= 20.10（可选）

### 后端启动

1. **安装依赖**

```bash
cd backend
pip install -r requirements.txt
```

2. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis、MinIO 等连接信息
```

3. **初始化数据库**

```bash
# 运行数据库迁移
alembic upgrade head

# 创建初始用户（可选）
python scripts/create_initial_users.py
```

4. **启动服务**

```bash
# 启动 FastAPI 服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动 Celery Worker（另开终端）
celery -A app.core.celery_app worker --loglevel=info

# 启动 Celery Flower（可选，监控任务）
celery -A app.core.celery_app flower --port=5555
```

### 前端启动

1. **安装依赖**

```bash
cd frontend
npm install
```

2. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，配置后端 API 地址
```

3. **启动开发服务器**

```bash
npm run dev
```

访问 http://localhost:3001 即可使用系统。

### Docker 快速启动

```bash
cd backend
docker-compose up -d
```

这将启动所有必需的服务（PostgreSQL、Redis、MinIO、后端 API、Celery Worker）。

## 用户角色

系统支持以下 6 种角色，每个角色有明确的职责分工：

| 角色 | 角色代码 | 职责描述 |
|------|----------|----------|
| **管理员** | `admin` | 系统管理、用户管理、系统配置管理 |
| **题目录入员** | `question_submitter` | 上传原始试题图片，创建新试题 |
| **OCR 编辑员** | `ocr_editor` | 校对 OCR 识别结果，修正识别错误 |
| **OCR 审核员** | `ocr_reviewer` | 审核 OCR 编辑结果，决定是否通过 |
| **改写编辑员** | `rewrite_editor` | 编辑 LLM 改写结果，或手动改写试题 |
| **改写审核员** | `rewrite_reviewer` | 审核改写结果，决定是否发布 |

### 角色权限说明

- **管理员**：拥有所有权限，可以管理用户、配置系统参数、查看所有数据
- **题目录入员**：只能上传图片和创建新试题，无法编辑或审核
- **OCR 编辑员**：可以编辑处于 OCR 编辑阶段的试题，提交给 OCR 审核员
- **OCR 审核员**：可以审核 OCR 编辑完成的试题，通过后进入改写阶段
- **改写编辑员**：可以编辑改写阶段的试题，触发 LLM 改写或手动改写
- **改写审核员**：可以审核改写完成的试题，通过后试题完成

## 试题处理流程

系统采用多阶段流程确保试题质量：
```
NEW（新建）
  │
  ├─→ [自动触发OCR任务]
  │
  ▼
OCR_编辑中
  │
  ├─→ [OCR编辑员提交]
  │   └─ 调用 markdown_to_required_format()
  │   └─ 自动分配审核员
  │
  ▼
OCR_待审
  │
  ├─→ [审核员批准] → OCR_通过
  │   └─ ocr_progress = 100%
  │   └─ 自动触发LLM任务
  │
  └─→ [审核员要求修改] → 返回 OCR_编辑中
  
OCR_通过
  │
  ├─→ [自动触发LLM任务]
  │
  ▼
改写_生成中
  │
  ├─→ [LLM生成5个版本]
  │
  ▼
改写_编辑中
  │
  ├─→ [改写编辑员提交所有版本]
  │   └─ 转换5个版本为单行格式
  │   └─ 自动分配审核员
  │
  ▼
改写_复审中
  │
  ├─→ [审核员批准所有5个版本] → DONE
  │   └─ rewrite_progress = 100%
  │
  └─→ [审核员要求修改某些版本] → 返回 改写_编辑中
```

### 状态流转说明

1. **NEW**：题目录入员上传图片后的初始状态
2. **OCR_编辑中**：OCR 识别完成，等待 OCR 编辑员校对
3. **OCR_待审**：OCR 编辑员提交后，等待 OCR 审核员审核
4. **OCR_通过**：OCR 审核通过，准备进入改写阶段
5. **改写_生成中**：LLM 正在生成改写版本
6. **改写_编辑中**：改写编辑员正在编辑
7. **改写_复审中**：改写审核员正在审核
8. **DONE**：所有流程完成，试题可以使用
9. **废弃**：试题被标记为废弃，不再使用

## 主要 API 端点

### 认证
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `GET /api/v1/auth/me` - 获取当前用户信息

### 试题
- `GET /api/v1/questions` - 获取试题列表
- `POST /api/v1/questions` - 创建新试题
- `GET /api/v1/questions/{id}` - 获取试题详情
- `PATCH /api/v1/questions/{id}` - 更新试题
- `POST /api/v1/questions/{id}/submit-ocr` - 提交 OCR 编辑
- `POST /api/v1/questions/{id}/review-ocr` - OCR 审核
- `POST /api/v1/questions/{id}/submit-rewrite` - 提交改写
- `POST /api/v1/questions/{id}/review-rewrite` - 改写审核
- `POST /api/v1/questions/{id}/trigger-llm-rewrite` - 触发 LLM 改写

### 上传
- `POST /api/v1/upload/image` - 上传图片

### 系统配置
- `GET /api/v1/system-config` - 获取系统配置
- `PUT /api/v1/system-config` - 更新系统配置

## 开发说明

### 代码规范

- 后端遵循 PEP 8 规范，使用 Black 进行代码格式化
- 前端使用 ESLint + TypeScript 严格模式
- 提交代码前请运行 lint 检查

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

## 部署

### 生产环境部署建议

1. 使用 Nginx 作为反向代理
2. 使用 Gunicorn + Uvicorn workers 运行后端
3. 前端构建后部署到 CDN 或静态服务器
4. 使用 Supervisor 或 systemd 管理进程
5. 配置日志收集和监控（推荐使用 Sentry）
6. 定期备份数据库

### 环境变量配置

详见 `backend/.env.example` 和 `frontend/.env.example`

主要配置项：
- 数据库连接
- Redis 连接
- MinIO/S3 配置
- JWT 密钥
- LLM API 配置
- OCR API 配置

## 常见问题

### Q: OCR 识别不准确怎么办？
A: 这正是系统设计 OCR 编辑员角色的原因。OCR 编辑员可以：
   - 手动校对 OCR 结果
   - 修正识别错误
   - 参考原始图片进行编辑
   - 使用 Markdown 格式重新编辑

### Q: 改写编辑员可以跳过 LLM 改写，直接手动改写吗？
A: 可以。改写编辑员既可以触发 LLM 自动改写，也可以直接手动编辑改写内容。

### Q: 如何切换不同的 LLM 服务？
A: 管理员可以在系统配置页面修改：
   - LLM API 端点
   - API 密钥
   - 提示词模板
   - 模型参数

### Q: 支持哪些图片格式？
A: 支持常见的图片格式：JPG、JPEG、PNG、WebP 等

### Q: 审核员拒绝了试题怎么办？
A: 审核员拒绝后，试题会退回到编辑阶段，由对应的编辑员重新编辑：
   - OCR 审核拒绝 → 退回 OCR 编辑员
   - 改写审核拒绝 → 退回改写编辑员

### Q: 题目录入员只能上传图片吗？
A: 是的。题目录入员的职责是上传原始试题图片和填写基本元信息（科目、年级、题型等），后续的编辑和审核由其他角色完成。

