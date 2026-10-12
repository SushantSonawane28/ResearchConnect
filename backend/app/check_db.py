"""Test your database connection.   python -m app.check_db"""
from sqlalchemy import inspect, text

from .database import engine

with engine.connect() as c:
    print("Connected to:", engine.dialect.name)
    if engine.dialect.name == "postgresql":
        print(c.execute(text("select version()")).scalar())
tables = inspect(engine).get_table_names()
print("Tables found:", len(tables), tables if tables else "(none yet - start the API once to create them)")
