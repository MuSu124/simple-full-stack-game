"""Django settings for the monster_game project.

Local-friendly defaults are kept here. Production differences and secrets are
read from environment variables so the same code can run safely on Render.
"""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    # 这是个工具函数，用于读取布尔类型的环境变量，例如true/false或1/0。
    """Read a boolean environment variable such as true/false or 1/0."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=None):
    # 这是个工具函数，用于读取逗号分隔的环境变量，并返回一个干净的列表。
    """Read a comma-separated environment variable into a clean list."""
    value = os.environ.get(name)
    if value is None:
        return list(default or [])
    return [item.strip() for item in value.split(",") if item.strip()]


# Local development is the default. Render must explicitly set DEBUG=false.
DEBUG = env_bool("DEBUG", default=True)

# The fallback key is only for local development. Production refuses to start
# without a secret supplied through the environment.
SECRET_KEY = os.environ.get("SECRET_KEY")
# secret key是django的密钥，用于加密和解密数据，必须保密，不能泄露。生产环境下必须设置SECRET_KEY，否则会抛出异常
# 之所以不在源代码中设置SECRET_KEY，是因为源代码可能会被公开，或者被多人使用，如果SECRET_KEY泄露，可能会导致数据被篡改或者泄露，所以生产环境下必须通过环境变量来设置SECRET_KEY
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-local-development-only"
    else:
        raise ImproperlyConfigured("SECRET_KEY must be set when DEBUG is false.")

ALLOWED_HOSTS = env_list(
    # 这个参数的本质是，允许哪些主机名可以访问这个django后端文件
    # 更详细地说，只有本地开发环境和Render平台的主机名可以访问这个django后端，其他主机名都会被拒绝访问（客户不应该直接访问后端，而是通过前端访问后端）
    # 所以这里会放localhost和render平台的主机名，render平台的主机名是通过环境变量RENDER_EXTERNAL_HOSTNAME获取的
    "ALLOWED_HOSTS",
    default=["127.0.0.1", "localhost"],
)

# Render provides this automatically for every web service.
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


INSTALLED_APPS = [
    # 这个参数是django的应用程序列表，包含了django自带的应用程序和我们自己创建的应用程序
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "characters",
]

MIDDLEWARE = [
    # 这个参数是django的中间件列表，中间件是处理请求和响应的钩子框架
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # CORS must run before middleware that can create a response, especially
    # CommonMiddleware, so error responses receive CORS headers too.
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "monster_game.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "monster_game.wsgi.application"


# Use local SQLite when DATABASE_URL is absent and Render PostgreSQL when it is
# present. Render supplies DATABASE_URL after the database is linked.
DATABASES = {
    # 这个参数用来放数据库的配置，默认是sqlite数据库，生产环境下使用PostgreSQL数据库
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# collectstatic copies all Django static assets here. WhiteNoise serves this
# directory when the application runs behind Gunicorn.
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# Vite's default development origins. Production origins should be provided as
# a comma-separated CORS_ALLOWED_ORIGINS environment variable on Render.

# 这个配置非常重要
# 在本地运行中，前后端的端口号不同，前端是5175，后端是8000，所以需要设置允许跨域访问的域名，否则前端无法访问后端的接口
LOCAL_FRONTEND_ORIGINS = [
    "http://localhost:5175",
    "http://127.0.0.1:5175",
]

CORS_ALLOWED_ORIGINS = env_list(
    # 这个参数是用来设置允许跨域访问的域名的，
    # 作用是：因为前后端部署在不同平台上，所以需要设置允许跨域访问的域名，否则前端无法访问后端的接口
    "CORS_ALLOWED_ORIGINS",
    default=LOCAL_FRONTEND_ORIGINS if DEBUG else [],
)
CORS_ALLOW_CREDENTIALS = True

# These become relevant when unsafe API requests use Django's CSRF protection.
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    default=LOCAL_FRONTEND_ORIGINS if DEBUG else [],
)

# Render terminates HTTPS before forwarding requests to Gunicorn. This header
# lets Django recognize the original request as secure.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# "Lax" is the safe default. If the deployed frontend and backend are truly
# cross-site, set both variables to None on Render and continue using HTTPS.
SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.environ.get("CSRF_COOKIE_SAMESITE", "Lax")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
