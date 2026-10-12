import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL, ENABLE_RLS

log = logging.getLogger(__name__)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:  # PostgreSQL (local Docker, Supabase, Render, Railway ...)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=5, pool_recycle=300)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def lock_down_postgres_tables() -> None:
    """SUPABASE SAFETY: Supabase can expose every table in the public schema through its own web API
    (with the public 'anon' key). Our app talks to the database ONLY through the FastAPI backend, so we turn on
    Row Level Security with NO policies: the public API sees nothing, while our backend (which connects as the
    owner role) keeps full access. Safe to run many times."""
    if engine.dialect.name != "postgresql" or not ENABLE_RLS:
        return
    try:
        with engine.begin() as conn:
            for table in Base.metadata.sorted_tables:
                conn.execute(text(f'ALTER TABLE "{table.name}" ENABLE ROW LEVEL SECURITY'))
    except Exception:
        log.warning("Could not enable row level security. Run docs/supabase_security.sql by hand.", exc_info=True)
