from sqlalchemy.orm import Session, sessionmaker

from database.connection import engine


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Session:
    """Create a database session for short-lived application work."""
    return SessionLocal()
