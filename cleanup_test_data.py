"""
Clean up test data from the database.
"""
import os
from dotenv import load_dotenv
from src.storage.sql.database import DatabaseClient

load_dotenv()

postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT", "5432")

database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

db = DatabaseClient(database_url=database_url)

print("Cleaning up test data...")

# Use session directly for DELETE operations
with db.get_session() as session:
    from sqlalchemy import text
    result = session.execute(text("DELETE FROM orders WHERE order_id LIKE 'TEST-%'"))
    deleted_count = result.rowcount
    print(f"✅ Deleted {deleted_count} test records")

counts = db.get_table_counts()
print(f"Current record count: {counts['orders']} orders")

db.close()
print("✅ Cleanup complete")
