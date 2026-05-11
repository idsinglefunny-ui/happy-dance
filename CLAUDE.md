# CLAUDE.md

## Project Overview

舞王 (Dance King) — 舞厅信息聚合平台，包含数据爬虫、API 后端、管理后台和微信小程序。

## Structure

```
backend/          — Python FastAPI backend (uvicorn, port 12800)
  api/main.py       — FastAPI app with all API routes
  crawler.py        — 数据抓取引擎 (从舞图图抓取)
  schema.sql        — MySQL schema
admin/            — Vue 3 + Vant 管理后台 (Vite build)
danceKing-ui/     — 微信小程序前端 (uni-app)
```

## Build & Run Commands

```bash
# Backend
cd backend
uv sync                                          # install deps (Python >=3.13, uses uv)
uvicorn api.main:app --host 0.0.0.0 --port 12800 # run dev server

# Admin frontend
cd admin
npm install && npx vite build                    # build to admin/dist/

# Run crawler manually
cd backend && python crawler.py
```

## Tech Stack

- **Backend**: Python 3.13, FastAPI, uvicorn, PyMySQL
- **Database**: MySQL 8.0+ (requires POINT SRID 4326 spatial index)
- **Admin**: Vue 3, Vant 4, Vite 8
- **Mini Program**: uni-app

## Deploy

**Production server:** `root@www.tangpinglife.com` (ssh-key login)

### Services

| Service | Domain | Port | Description |
|---------|--------|------|-------------|
| Backend API | `https://dance.tangpinglife.com` | 12800 (behind nginx) | FastAPI |
| Admin | `https://dance-admin.tangpinglife.com` | nginx static + API proxy | Vue SPA |

### Deploy Paths on Server

| Component | Path |
|-----------|------|
| Backend code | `/root/happy-dance/backend/` |
| Backend .env | `/root/happy-dance/backend/.env` |
| Admin dist | `/root/happy-dance/admin/dist/` |
| Systemd service | `/etc/systemd/system/happy-dance.service` |
| Nginx config | `/etc/nginx/conf.d/dance.tangpinglife.com.conf` |
| SSL certs | `/etc/nginx/ssl/dance.tangpinglife.com/` and `/etc/nginx/ssl/dance-admin.tangpinglife.com/` |
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
scp /path/to/happy-dance/backend/api/main.py root@www.tangpinglife.com:/root/happy-dance/backend/api/
scp /path/to/happy-dance/backend/crawler.py root@www.tangpinglife.com:/root/happy-dance/backend/
ssh root@www.tangpinglife.com "systemctl restart happy-dance"

# Deploy admin (build locally + upload + fix permissions)
cd admin && npm install && npx vite build
scp -r dist/* root@www.tangpinglife.com:/root/happy-dance/admin/dist/
ssh root@www.tangpinglife.com "chmod -R 755 /root/happy-dance/admin/dist"
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
- Both `dance.tangpinglife.com` and `dance-admin.tangpinglife.com` proxy `/api/` to backend port 12800
