# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

舞王 (Dance King) — 舞厅信息聚合平台，包含数据爬虫、API 后端、管理后台和微信小程序。

## Structure

```
backend/          — Python FastAPI backend (uvicorn, port 12800)
  api/main.py       — FastAPI app with all API routes + middleware (monolithic, ~360 lines)
  api/security.py   — 签名验证 + AES-256-CBC 加解密
  crawler.py        — 数据抓取引擎 (从舞图图 api.dancehallmap.com 抓取)
  init_db.py        — 初始化数据库 (创建表)
  schema.sql        — MySQL schema (不含 dance_hall_reports 表，该表在 app 启动时动态创建)
admin/            — Vue 3 + Vant 管理后台 (Vite build)
miniprogram/      — 微信小程序前端 (uni-app 3.0)
  src/config.js      — API 地址配置 (根据 Vite 环境变量自动切换)
  src/request.js     — 请求封装（自动签名 + 加密/解密）
  src/crypto.js      — MD5 + AES（与 backend/api/security.py 对应）
```

## Build & Run Commands

```bash
# Backend
cd backend
uv sync                                          # install deps (Python >=3.13, uses uv)
uvicorn api.main:app --host 0.0.0.0 --port 12800 # run dev server

# Initialize database
cd backend && python init_db.py

# Run crawler manually
cd backend && python crawler.py

# Admin frontend
cd admin
npm install && npx vite build                    # build to admin/dist/

# Mini Program (微信小程序)
cd miniprogram
npm install
npx uni -p mp-weixin                    # 开发模式 → dist/dev/mp-weixin/
npx uni build -p mp-weixin              # 生产构建 → dist/build/mp-weixin/
```

## Testing

No test framework is configured. Two manual test scripts exist:

```bash
cd backend
python -m api.test_api               # FastAPI TestClient tests (GET /api/dance-halls, POST /api/claims)
python test_api.py                    # Standalone script testing external API connectivity
```

## Mini Program Environment Config

`src/config.js` 根据 Vite 环境变量自动切换后端地址：

| Command | `import.meta.env.DEV` | API Base URL |
|---------|-----------------------|--------------|
| `uni -p mp-weixin` | `true` | `http://localhost:12800` |
| `uni build -p mp-weixin` | `false` | `https://dance.index-tts.cn` |

所有页面通过 `import BASE_URL from '@/config.js'` 引用，不直接硬编码地址。

## Tech Stack

- **Backend**: Python 3.13, FastAPI, uvicorn, PyMySQL
- **Database**: MySQL 8.0+ (requires POINT SRID 4326 spatial index)
- **Admin**: Vue 3, Vant 4, Vite 8
- **Mini Program**: uni-app 3.0, crypto-js

## API Security

小程序访问 `/api/` 接口（`/api/admin/` 除外）需要签名验证，响应数据经过加密。

### 请求签名

每个请求必须携带三个额外参数：

| 参数 | 说明 |
|------|------|
| `t` | 当前时间戳（秒） |
| `nonce` | 6位随机字符串 |
| `sign` | MD5 签名 |

签名算法：`sign = MD5(所有参数按key排序拼接 + key=SECRET_KEY)`

服务端校验：时间戳偏差 ≤ 5 分钟 + 签名一致，否则返回 403。

### 响应加密

- 算法：AES-256-CBC
- 响应格式：`{"data": "base64加密字符串"}`
- 客户端自动解密后得到原始 JSON

### POST 请求

POST 请求的 body 通过 AES 加密后以 `{"_encrypted": "base64密文"}` 发送，签名参数附在 query string。

### 代码位置

| 文件 | 说明 |
|------|------|
| `backend/api/security.py` | 签名验证 + AES 加解密 |
| `backend/api/main.py` | SecurityMiddleware 中间件 |
| `miniprogram/src/crypto.js` | MD5 + AES（基于 crypto-js） |
| `miniprogram/src/request.js` | 请求封装（自动签名 + 解密） |

### 豁免路由

`/api/admin/*` 路由不走签名验证，由 nginx Basic Auth 保护。

## Deploy

**Production server:** `root@8.138.80.202` / `root@dance.index-tts.cn` (ssh-key login)

### Services

| Service | Domain | Port | Description |
|---------|--------|------|-------------|
| Backend API | `https://dance.index-tts.cn` | 12800 (behind nginx) | FastAPI |
| Admin | `https://dance-admin.index-tts.cn` | nginx static + API proxy | Vue SPA |

### Deploy Paths on Server

| Component | Path |
|-----------|------|
| Backend code | `/root/happy-dance/backend/` |
| Backend .env | `/root/happy-dance/backend/.env` |
| Admin dist | `/root/happy-dance/admin/dist/` |
| Systemd service | `/etc/systemd/system/happy-dance.service` |
| Nginx config | `/etc/nginx/conf.d/dance.conf` |
| SSL certs | `/etc/nginx/ssl/dance.index-tts.cn/` and `/etc/nginx/ssl/dance-admin.index-tts.cn/` |
| htpasswd | `/etc/nginx/.htpasswd-dance-admin` |

### Admin Authentication

Admin 后台使用 nginx HTTP Basic Auth 保护：
- 用户名: `admin`
- 密码: `dance2026_go`
- 修改密码: `htpasswd -bc /etc/nginx/.htpasswd-dance-admin admin '新密码'`

### Database

External MySQL at `117.72.76.53:63306`, database `king_dance`.

### Build & Deploy (from local machine)

```bash
# Deploy backend (upload code + restart)
scp /path/to/happy-dance/backend/api/main.py root@dance.index-tts.cn:/root/happy-dance/backend/api/
scp /path/to/happy-dance/backend/crawler.py root@dance.index-tts.cn:/root/happy-dance/backend/
ssh root@dance.index-tts.cn "systemctl restart happy-dance"

# Deploy admin (build locally + upload + fix permissions)
cd admin && npm install && npx vite build
scp -r dist/* root@dance.index-tts.cn:/root/happy-dance/admin/dist/
ssh root@dance.index-tts.cn "chmod -R 755 /root/happy-dance/admin/dist"
```

### Systemd Service Management

```bash
systemctl status happy-dance       # check status
journalctl -u happy-dance -f       # follow logs
systemctl restart happy-dance      # restart
```

### Notes

- Server has only 1.8GB RAM — Python runs fine, no need to build locally
- uv is installed at `/root/.local/bin/uv` with Aliyun PyPI mirror configured in `backend/uv.toml`
- SSL certs auto-renew via acme.sh
- Both `dance.index-tts.cn` and `dance-admin.index-tts.cn` proxy `/api/` to backend port 12800
