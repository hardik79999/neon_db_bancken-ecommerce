import asyncio
import sys
from contextlib import asynccontextmanager

from flask import current_app
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()


def configure_asyncio_policy():
    if sys.platform.startswith("win") and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        current_policy = asyncio.get_event_loop_policy()
        if not isinstance(current_policy, asyncio.WindowsSelectorEventLoopPolicy):
            # psycopg async connections require the selector loop on Windows.
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def init_async_db(app):
    async_database_uri = app.config.get("SQLALCHEMY_ASYNC_DATABASE_URI")
    if not async_database_uri:
        return

    configure_asyncio_policy()

    # Keep a dedicated async engine/sessionmaker beside Flask-SQLAlchemy's sync engine.
    async_engine = create_async_engine(
        async_database_uri,
        echo=app.config.get("SQLALCHEMY_ECHO", False),
        **app.config.get("SQLALCHEMY_ASYNC_ENGINE_OPTIONS", {}),
    )
    app.extensions["sqlalchemy_async_engine"] = async_engine
    app.extensions["sqlalchemy_async_sessionmaker"] = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def get_async_engine():
    async_engine = current_app.extensions.get("sqlalchemy_async_engine")
    if async_engine is None:
        raise RuntimeError("Async SQLAlchemy engine is not initialized. Call init_async_db(app) first.")
    return async_engine


def get_async_sessionmaker():
    session_factory = current_app.extensions.get("sqlalchemy_async_sessionmaker")
    if session_factory is None:
        raise RuntimeError("Async SQLAlchemy sessionmaker is not initialized. Call init_async_db(app) first.")
    return session_factory


@asynccontextmanager
async def get_async_session():
    session_factory = get_async_sessionmaker()
    async with session_factory() as session:
        yield session


async def dispose_async_engine(app):
    async_engine = app.extensions.get("sqlalchemy_async_engine")
    if async_engine is not None:
        await async_engine.dispose()
