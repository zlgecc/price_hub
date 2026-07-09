# 价格中心 Price Hub

每日价格聚合平台 — 贵金属、油价、生活必需品、大宗商品、汇率、股票指数与科技芯片。用户可浏览价格并订阅感兴趣的项目，在个人中心查看（MVP 阶段订阅存 localStorage）。

## 项目结构

```
price_hub/
├── api/        # Vercel Python 入口
├── client/     # React 前端
├── server/     # FastAPI 后端
├── docs/       # 文档
└── .github/    # CI 与定时抓价
```

## 本地开发

### 前置要求

- Docker Desktop（PostgreSQL）
- Python 3.12+
- Node.js 20+

### 1. 启动数据库（可选，使用 Postgres 时）

```bash
docker compose up -d postgres
```

默认本地开发使用 SQLite（`sqlite:///./price_hub.db`），启动后端时会自动建表并种子数据，无需手动执行 `alembic` / `seed`。

若使用 Postgres，设置 `DATABASE_URL=postgresql://pricehub:pricehub@localhost:5432/price_hub` 后执行：

```bash
alembic upgrade head
python -m app.seed
```

### 2. 后端

```bash
cd server
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

API 文档：http://127.0.0.1:8001/docs

### 3. 前端

```bash
cd client
cp .env.example .env
npm install
npm run dev
```

访问：http://127.0.0.1:5173

> 开发模式下前端通过 Vite 代理访问后端，请保持 `VITE_API_BASE_URL` 为空；代理目标为 `127.0.0.1:8001`（避免本机 8000 被其他服务占用）。

### 4. 手动触发抓价

```bash
curl -X POST http://127.0.0.1:8001/internal/fetch \
  -H "Authorization: Bearer dev-secret-change-in-production"
```

## 环境变量

| 变量 | 说明 | 必填 |
|------|------|------|
| `DATABASE_URL` | 数据库连接串，默认 SQLite | 否 |
| `CRON_SECRET` | 定时任务鉴权密钥 | 是 |
| `FRED_API_KEY` | FRED API（国际大宗/WTI，可选；无 Key 走公开 CSV） | 可选 |
| `TIANAPI_KEY` | 天聚数行（国内省油价，可选；无 Key 走东方财富） | 可选 |
| `CORS_ORIGINS` | 前端域名，逗号分隔 | 是 |

## 部署

详见 [docs/deployment.md](docs/deployment.md)

**推荐（最快上线）**：Vercel + SQLite（自动建表/种子数据，无需 Neon）

1. 在 [Vercel](https://vercel.com/) 导入 GitHub 仓库
2. 配置环境变量 `CRON_SECRET`、`CORS_ORIGINS`
3. 部署后访问 `https://你的项目.vercel.app`，再手动触发一次抓价

### 单镜像部署（Docker）

项目根目录提供了多阶段 `Dockerfile`，会自动构建前端并由 FastAPI 同容器托管静态资源与 API。

```bash
docker build -t price-hub:latest .
docker run -d --name price-hub \
  -p 8080:8080 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require" \
  -e CRON_SECRET="your-secret" \
  -e CORS_ORIGINS="http://localhost:8080" \
  price-hub:latest
```

访问：`http://localhost:8080`（前端）和 `http://localhost:8080/docs`（API 文档）。

## 数据源

详见 [docs/data-sources.md](docs/data-sources.md)

## License

MIT
