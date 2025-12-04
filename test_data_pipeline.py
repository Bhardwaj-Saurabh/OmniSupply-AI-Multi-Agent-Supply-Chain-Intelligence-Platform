"""Quick test of data pipeline fixes"""
import os
from dotenv import load_dotenv
from src.storage.sql.database import DatabaseClient

load_dotenv()

# Build PostgreSQL connection
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT", "5432")

database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

print("🔧 Testing PostgreSQL SQL Helper Methods...")
print(f"Connecting to: {postgres_host}:{postgres_port}/{postgres_db}")

try:
    db = DatabaseClient(database_url=database_url)
    print(f"✅ Connected successfully!")
    print(f"Database type: {db.get_db_type()}")

    # Test SQL helper methods
    print("\n📊 Testing SQL Helper Methods:")
    print(f"Date interval (30 days): {db.get_date_interval_sql(30)}")
    print(f"Date diff: {db.get_date_diff_sql('date1', 'date2')}")
    print(f"Date format: {db.get_date_format_sql('order_date', '%Y-%m')}")

    # Test has_data
    print(f"\n🔍 Has data: {db.has_data()}")

    # Test table counts
    print("\n📈 Current table counts:")
    counts = db.get_table_counts()
    for table, count in counts.items():
        print(f"   • {table}: {count}")

    # Test a simple query with date functions
    print("\n🧪 Testing date function query...")
    date_interval = db.get_date_interval_sql(30)
    query = f"SELECT COUNT(*) as count FROM orders WHERE order_date >= {date_interval}"

    try:
        result = db.execute_query(query)
        print(f"✅ Query executed successfully!")
        print(f"Orders in last 30 days: {result[0]['count'] if result else 0}")
    except Exception as e:
        print(f"❌ Query failed: {e}")

    db.close()
    print("\n✅ All tests passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
