# 本地部署（WSL2 + Docker）

二开工作树：`/home/pg/workspace/github/个人/openGym`
部署产物目录：`/home/pg/workspace/github/个人/openGym-deploy/out`（APK，不进仓库）

## 容器

```bash
cd "/home/pg/workspace/github/个人/openGym"
sg docker -c 'docker compose up -d --build'   # 从本仓库源码构建
sg docker -c 'docker compose ps'
sg docker -c 'docker compose logs -f api'
```

| 项 | 值 |
| --- | --- |
| 服务 | `opengym-api-1`（Node :8787）+ `opengym-web-1`（nginx 80→宿主 8080） |
| 镜像 | `opengym-fork/api:local`、`opengym-fork/web:local`（**fork 专属 tag**） |
| 数据 | `./data`（root 所有，gitignored）：用户、passkey、secret、vapid |
| 本地 | http://127.0.0.1:8080 |
| 公网 | https://gym.gzg666.dpdns.org（cloudflared tunnel `docker`） |
| APK | https://apk.gzg666.dpdns.org → `opengym-apk.service` → `openGym-deploy/out` (127.0.0.1:18090) |

## 为什么镜像用 fork 专属 tag

`docker-compose.yml` 里 `api.image` / `web.image` 指向上游 ghcr。`docker compose up --build` 会用同名 tag 覆盖本地镜像，
之后任何人跑一次 `docker compose pull` 就把上游镜像拉回来盖掉我们的构建 —— 二开代码静默消失。

因此本地加了 `docker-compose.override.yml`（**不进版本控制**，已写入 `.git/info/exclude`）：

```yaml
services:
  api: { image: opengym-fork/api:local }
  web: { image: opengym-fork/web:local }
```

改了二开代码后的重建：

```bash
sg docker -c 'docker compose build api web && docker compose up -d'
```

## 构建注意

- `api` 的 `RUN apk upgrade --no-cache` 偶发 `TLS: unspecified error`（buildkit 拉 Alpine CDN 抖动），**直接重跑一次即可**，不要改 Dockerfile。
- 构建需要外网（npm registry / Alpine）。当前容器网络直连可用，无需给 docker daemon 配代理。
- 前端构建在镜像内 `npm ci`，宿主的 `frontend/node_modules` 不参与。

## 升级上游

```bash
bash .fork/bin/fork-sync.sh --check
bash .fork/bin/fork-sync.sh --apply        # rebase patch 层
sg docker -c 'docker compose build api web && docker compose up -d'
bash .fork/bin/fork-doctor.sh
```

## passkey 相关

`RP_ID` / `ORIGIN` 必须与实际访问域名一致（见 `.env`）。用 `http://localhost:8080` 直接访问时 passkey 会失败，
走公网域名或 `PASSWORD_LOGIN=1` 的密码登录。
