# Django settings 配置说明

项目使用同一份 `monster_game/settings.py` 支持本地开发和 Render 部署：

- 本地：`DEBUG=True`，使用 SQLite，允许 Vite 本地地址访问 API。
- Render：`DEBUG=False`，使用 PostgreSQL，密钥和域名从环境变量读取。

## 核心配置

### `BASE_DIR`

指向 `backend/` 目录，用来构造 SQLite 和静态文件路径，避免写死电脑上的绝对路径。

### `DEBUG`

通过环境变量读取。本地默认为 `True`；Render 必须设置为 `false`，防止调试页暴露配置和错误细节。

### `SECRET_KEY`

用于 Django 签名和 Session 安全。本地使用临时值；生产环境必须从 Render 环境变量提供，否则项目拒绝启动。真实密钥不能提交到 Git。

### `ALLOWED_HOSTS`

限制允许访问 Django 的主机名。本地允许 `localhost` 和 `127.0.0.1`；Render 的 `RENDER_EXTERNAL_HOSTNAME` 会被自动加入。自定义后端域名可通过 `ALLOWED_HOSTS` 环境变量添加。

### `INSTALLED_APPS`

- `corsheaders`：让 Vue 可以跨域访问 API。
- `django.contrib.*`：Django 自带的用户、Session、Admin 和静态文件功能。
- `accounts`、`characters`：项目自己的 Django app。

### `MIDDLEWARE`

中间件顺序有意义：

- `SecurityMiddleware`：处理常规安全头。
- `WhiteNoiseMiddleware`：Gunicorn 运行时提供 Django 静态文件。
- `CorsMiddleware`：添加 CORS 响应头，必须放在 `CommonMiddleware` 前面。
- Session、CSRF 和 Authentication 中间件分别负责登录状态、防止跨站写请求和设置 `request.user`。

### `DATABASES`

`dj_database_url` 将 `DATABASE_URL` 转换为 Django 数据库配置：

- 没有 `DATABASE_URL`：本地使用 `backend/db.sqlite3`。
- 有 `DATABASE_URL`：Render 上自动使用 PostgreSQL。
- `conn_max_age=600`：复用数据库连接 600 秒。
- `conn_health_checks=True`：复用前检查连接是否可用。

Render 默认文件系统不适合用 SQLite 持久保存用户数据，所以线上使用 PostgreSQL。

### 静态文件

- `STATIC_URL`：浏览器中的静态文件 URL 前缀。
- `STATIC_ROOT`：`collectstatic` 收集文件的目录。
- `CompressedManifestStaticFilesStorage`：压缩文件并使用内容哈希文件名，方便缓存。

WhiteNoise 只处理 Django Admin 和 Django app 的静态文件。Vue 构建结果由前端服务单独托管，用户上传文件也不应交给 WhiteNoise。

### CORS 和 CSRF

`CORS_ALLOWED_ORIGINS` 决定哪些 Vue 网址能在浏览器中请求 API。本地默认允许 Vite 的 `localhost:5173` 和 `127.0.0.1:5173`；生产环境必须明确提供前端 URL。

`CORS_ALLOW_CREDENTIALS=True` 允许跨域携带 Session Cookie，但 Vue `fetch` 也必须设置 `credentials: "include"`。

`CSRF_TRUSTED_ORIGINS` 是可以发起受 CSRF 保护写请求的可信前端。当前部分 API 使用 `@csrf_exempt`，正式上线前应移除豁免并补上 CSRF Token 流程。

### HTTPS 和 Cookie

- `SECURE_PROXY_SSL_HEADER`：让 Django 正确识别 Render 反向代理前的 HTTPS 请求。
- `SECURE_SSL_REDIRECT`：生产环境将 HTTP 请求转到 HTTPS，本地开发时关闭。
- `SESSION_COOKIE_SECURE` 和 `CSRF_COOKIE_SECURE`：生产环境只允许 HTTPS 发送 Cookie。
- `SESSION_COOKIE_SAMESITE` 和 `CSRF_COOKIE_SAMESITE`：默认为 `Lax`。如果前后端被浏览器视为不同 site，Render 中需设为 `None`，并且必须使用 HTTPS。

## Render 环境变量

创建后端 Web Service 时至少设置：

```text
DEBUG=false
SECRET_KEY=<Render 生成的随机值>
DATABASE_URL=<Render PostgreSQL 连接地址>
```

前端部署后再设置：

```text
CORS_ALLOWED_ORIGINS=https://<前端域名>
CSRF_TRUSTED_ORIGINS=https://<前端域名>
```

`RENDER_EXTERNAL_HOSTNAME` 由 Render 自动提供，不需要手动添加。

## 验证配置

```bash
cd backend
source .venv/bin/activate
python manage.py check
python manage.py runserver
```

生产模式检查：

```bash
DEBUG=false SECRET_KEY=test-only-secret \
RENDER_EXTERNAL_HOSTNAME=example.onrender.com \
python manage.py check --deploy
```
