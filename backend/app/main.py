from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401  (registers the tables)
from .config import CORS_ORIGINS
from .database import Base, engine, lock_down_postgres_tables
from .routers import admin, alerts, auth, match, opportunities, profiles, projects, requests

Base.metadata.create_all(bind=engine)   # creates tables on first start
lock_down_postgres_tables()             # PostgreSQL/Supabase only: blocks the public Data API

app = FastAPI(title="ResearchConnect (PRAYAS) API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
for r in (auth, profiles, projects, match, requests, opportunities, admin, alerts):
    app.include_router(r.router)


@app.get("/")
def health():
    return {"status": "ok", "docs": "/docs"}
