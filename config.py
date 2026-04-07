import os
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv

load_dotenv()


_POSTGRES_SCHEME_RE = re.compile(r"^postgres(?:ql)?(?:\+[a-z0-9_]+)?://", re.IGNORECASE)


def _get_database_url():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return None

    # Accept quoted values in .env and normalize them before SQLAlchemy sees the URL.
    return database_url.strip().strip("\"'")


def _build_postgres_uri(driver_scheme):
    database_url = _get_database_url()
    if not database_url:
        return None

    normalized_url = _POSTGRES_SCHEME_RE.sub(f"{driver_scheme}://", database_url, count=1)
    parsed_url = urlsplit(normalized_url)
    query_params = dict(parse_qsl(parsed_url.query, keep_blank_values=True))

    # Neon pooled connections should always enforce TLS.
    query_params.setdefault("sslmode", "require")
    # psycopg supports channel binding, which matches the Neon connection string.
    query_params.setdefault("channel_binding", "require")

    return urlunsplit(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            urlencode(query_params),
            parsed_url.fragment,
        )
    )


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_fallback_secret_key"

    # Flask-SQLAlchemy and Flask-Migrate still use a standard SQLAlchemy engine.
    SQLALCHEMY_DATABASE_URI = _build_postgres_uri("postgresql+psycopg")
    # Async scripts/services can reuse the same Neon connection through AsyncEngine.
    SQLALCHEMY_ASYNC_DATABASE_URI = _build_postgres_uri("postgresql+psycopg")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_ASYNC_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO", "False") == "True"

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "hardik_jwt_super_secret_key"

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")



    # 📁 File Upload Settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "shop", "static", "uploads", "products")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
