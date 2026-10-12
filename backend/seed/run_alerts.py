"""Demo helper: run match alerts for every seeded user.   python -m seed.run_alerts
In DEV MODE (no SMTP_HOST) the emails appear as .eml files in backend/outbox/."""
from app.alerts import run_match_alerts
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
total = 0
for (uid,) in db.query(User.id).filter(User.role != "admin").all():
    total += run_match_alerts(uid, db)
print(f"Done. {total} new matches emailed to both sides. Check backend/outbox/")
db.close()
