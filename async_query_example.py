import asyncio

from sqlalchemy import select, text

from app import app
from shop.extensions import configure_asyncio_policy, dispose_async_engine, get_async_engine, get_async_session
from shop.models import User


async def run_example():
    try:
        with app.app_context():
            async_engine = get_async_engine()

            # Quick connectivity check against Neon over SQLAlchemy's async engine.
            async with async_engine.connect() as connection:
                result = await connection.execute(text("select 'hello world' as message"))
                print(result.scalar_one())

            # Example async ORM query using the existing Flask-SQLAlchemy model definitions.
            async with get_async_session() as session:
                users = (await session.execute(select(User).order_by(User.id).limit(5))).scalars().all()
                print([{"id": user.id, "email": user.email} for user in users])
    finally:
        await dispose_async_engine(app)


if __name__ == "__main__":
    configure_asyncio_policy()
    asyncio.run(run_example())
