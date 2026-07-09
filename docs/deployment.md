# 部署指南

## 推荐方案（Stack A，$0/月）

| 组件 | 服务 | 说明 |
|------|------|------|
| 前端 | Cloudflare Pages | 连接 GitHub 自动部署 `client/` |
| 后端 | Northflank | 512MB RAM，始终在线 |
| 数据库 | Neon | 0.5GB 永久免费 Postgres |
| 定时任务 | GitHub Actions | 每日 POST 触发抓价 |

## 1. GitHub 仓库

```bash
git init
git add .
git commit -m "Initial commit: Price Hub MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/price_hub.git
git push -u origin main
```

## 2. Neon 数据库

1. 注册 https://neon.tech/
2. 创建项目，获取连接串
3. 格式：`postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`

## 3. Northflank 后端

1. 注册 https://northflank.com/
2. 创建 Service，连接 GitHub 仓库
3. 构建配置：
   - Build context: `server/`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
4. 环境变量：

```
DATABASE_URL=postgresql://...
CRON_SECRET=your-random-secret
FRED_API_KEY=...
TIANAPI_KEY=...
CORS_ORIGINS=https://your-pages.pages.dev
```

5. 部署后运行迁移（一次性）：

```bash
alembic upgrade head
python -m app.seed
```

## 4. Cloudflare Pages 前端

1. 注册 https://pages.cloudflare.com/
2. 连接 GitHub 仓库
3. 构建设置：
   - Framework preset: Vite
   - Root directory: `client`
   - Build command: `npm run build`
   - Output directory: `dist`
4. 环境变量：

```
VITE_API_BASE_URL=https://your-api.northflank.app
```

## 5. GitHub Actions Secrets

在仓库 Settings → Secrets 中添加：

| Secret | 值 |
|--------|-----|
| `CRON_SECRET` | 与后端相同 |
| `API_BASE_URL` | Northflank 后端 URL |

Workflow 文件：`.github/workflows/fetch-prices.yml`

## 备选方案

### 国内用户为主

- 腾讯云 SCF（函数计算）+ 定时触发器
- 新用户约 3 个月免费

### 零运维、最大算力

- Oracle Cloud Always Free ARM VM（2 OCPU / 12GB）
- 自托管 Nginx + FastAPI + PostgreSQL + crontab

### 单平台

- Northflank 同时部署前端 + 后端 + DB + cron

## 不推荐

- Render 免费 Postgres（30 天过期）
- Railway 免费额度（$1/月不够用）
- Fly.io 新用户（仅试用）
- Cloudflare Workers 跑 Python 抓取（10ms CPU 限制）

## 部署后验证

1. 访问前端首页，确认 API 连通
2. 手动触发 GitHub Actions workflow `Daily Price Fetch`
3. 检查首页是否显示最新价格
4. 测试订阅功能（localStorage）
