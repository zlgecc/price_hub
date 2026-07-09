# 部署指南

## 推荐方案：Vercel 单项目（最简单）

前端静态页 + Python API 部署在同一个 Vercel 项目，访问一个域名即可打开页面。

| 组件 | 服务 | 说明 |
|------|------|------|
| 前端 + API | Vercel | `client/dist` 静态资源 + `api/index.py` FastAPI |
| 数据库 | Neon | 0.5GB 永久免费 Postgres |
| 定时任务 | GitHub Actions | 每日 POST 触发抓价 |

### 1. 准备数据库（Neon）

1. 注册 https://neon.tech/
2. 创建项目，复制连接串：
   `postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`
3. 本地或 CI 执行一次性初始化：

```bash
cd server
pip install -r requirements.txt
export DATABASE_URL="postgresql://..."
alembic upgrade head
python -m app.seed
```

### 2. 部署到 Vercel

1. 注册 https://vercel.com/ ，导入 GitHub 仓库 `zlgecc/price_hub`
2. 保持默认构建设置（项目根目录已有 `vercel.json`）：
   - Build command: `npm run build`
   - Output directory: `client/dist`
3. 在 Vercel 项目 **Settings → Environment Variables** 添加：

| 变量 | 值 |
|------|-----|
| `DATABASE_URL` | Neon 连接串 |
| `CRON_SECRET` | 随机密钥 |
| `CORS_ORIGINS` | `https://你的项目.vercel.app` |
| `FRED_API_KEY` | 可选 |
| `TIANAPI_KEY` | 可选 |

> 前端与 API 同域，**不要**设置 `VITE_API_BASE_URL`，页面会通过相对路径访问 `/api/*`。

4. 点击 Deploy，完成后访问 `https://你的项目.vercel.app` 即可看到页面。

### 3. GitHub Actions 定时抓价

在仓库 Settings → Secrets 中添加：

| Secret | 值 |
|--------|-----|
| `CRON_SECRET` | 与 Vercel 相同 |
| `API_BASE_URL` | `https://你的项目.vercel.app` |

### 注意事项

- Vercel Python 为 Serverless，冷启动会有几秒延迟。
- `/internal/fetch` 抓价任务受函数超时限制（默认 60 秒，可在 `vercel.json` 调整）。
- 依赖包含 `pandas` / `akshare`，部署包较大；若构建失败，可考虑升级 Vercel 套餐或改用 Docker 部署。

---

## 备选方案（Stack A，$0/月）

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
