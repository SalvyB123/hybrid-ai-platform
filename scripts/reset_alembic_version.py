import os

from sqlalchemy import create_engine, text

# Use the same DATABASE_URL your app uses, e.g.
# export DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    raise SystemExit("❌ DATABASE_URL not set in environment")

# For SQLAlchemy engine, strip async driver if present
db_url_sync = db_url.replace("+asyncpg", "")

engine = create_engine(db_url_sync, isolation_level="AUTOCOMMIT")

with engine.begin() as conn:
    # Clear the stale row
    conn.execute(text("DELETE FROM alembic_version;"))
    # Stamp to your last valid migration (bookings)
    conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('1130532299a8');"))

print("✅ alembic_version table reset to 1130532299a8")
