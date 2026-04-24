from app.db import models  # noqa: F401
from app.db.session import Base, engine


def init_db() -> None:
    """Create tables for local MVP use; Alembic is preferred for shared DBs."""

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
