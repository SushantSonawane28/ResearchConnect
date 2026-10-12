import os
from dotenv import load_dotenv

load_dotenv()

def normalize_db_url(url: str) -> str:
    """Supabase/Render/Railway give URLs starting with postgres:// or postgresql://.
    SQLAlchemy needs the driver name, so we add it. SQLite URLs are left alone."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg2://" + url[len(prefix):]
    return url


DATABASE_URL = normalize_db_url(os.getenv("DATABASE_URL", "sqlite:///./prayas.db"))
ENABLE_RLS = os.getenv("ENABLE_RLS", "true").lower() == "true"   # lock Supabase's public Data API (see README)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me")
TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "120"))
APP_ENV = os.getenv("APP_ENV", "development").lower()
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]

# --- Email alerts ---
SMTP_HOST = os.getenv("SMTP_HOST", "")            # empty = DEV MODE: emails are saved to backend/outbox/ instead of sent
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_TLS = os.getenv("SMTP_TLS", "true").lower() == "true"
SMTP_FROM = os.getenv("SMTP_FROM", "ResearchConnect <no-reply@researchconnect.local>")
APP_URL = os.getenv("APP_URL", "http://localhost:5173")
MATCH_ALERT_THRESHOLD = float(os.getenv("MATCH_ALERT_THRESHOLD", "0.30"))  # hybrid score needed to send an alert
MATCH_ALERT_MAX = int(os.getenv("MATCH_ALERT_MAX", "3"))                    # max new alerts per trigger, avoids spam
