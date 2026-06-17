"""Run this once to initialise the database schema."""
import psycopg2
from pathlib import Path

DB_URL = "postgresql://postgres:password@localhost:5432/anomaly_db"

def init():
    sql = Path("schema.sql").read_text()
    conn = psycopg2.connect(DB_URL)
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    conn.close()
    print("Database initialised.")

if __name__ == "__main__":
    init()
