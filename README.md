# 价格中心 Price Hub

每日价格聚合平台 — 贵金属、油价、生活必需品、大宗商品、汇率、股票指数与科技芯片。用户可浏览价格并订阅感兴趣的项目，在个人中心查看（MVP 阶段订阅存 localStorage）。

## 项目结构

```
price_hub/
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

### 1. 启动数据库

```bash
docker compose up -d postgres
```

### 2. 后端

```bash
cd server
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
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
| `DATABASE_URL` | PostgreSQL 连接串 | 是 |
| `CRON_SECRET` | 定时任务鉴权密钥 | 是 |
| `FRED_API_KEY` | FRED API（国际大宗/WTI，可选；无 Key 走公开 CSV） | 可选 |
| `TIANAPI_KEY` | 天聚数行（国内省油价，可选；无 Key 走东方财富） | 可选 |
| `CORS_ORIGINS` | 前端域名，逗号分隔 | 是 |

## 部署

详见 [docs/deployment.md](docs/deployment.md)

推荐免费方案：Cloudflare Pages（前端）+ Northflank（后端）+ Neon（数据库）+ GitHub Actions（定时抓价）

## 数据源

详见 [docs/data-sources.md](docs/data-sources.md)

## License

MIT
