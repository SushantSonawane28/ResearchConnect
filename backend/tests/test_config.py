from app.config import normalize_db_url


def test_supabase_urls_get_driver():
    assert normalize_db_url("postgres://u:p@h:5432/db") == "postgresql+psycopg2://u:p@h:5432/db"
    assert normalize_db_url("postgresql://u:p@h:5432/db") == "postgresql+psycopg2://u:p@h:5432/db"


def test_other_urls_unchanged():
    assert normalize_db_url("sqlite:///./prayas.db") == "sqlite:///./prayas.db"
    assert normalize_db_url("postgresql+psycopg2://u:p@h/db") == "postgresql+psycopg2://u:p@h/db"
