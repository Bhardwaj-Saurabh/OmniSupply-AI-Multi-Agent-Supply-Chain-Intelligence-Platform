"""
Schema migration script to update is_returned from INTEGER to BOOLEAN.

Run this script if you have existing data in PostgreSQL and need to migrate the schema.
"""
import os
from dotenv import load_dotenv
from src.storage.sql.database import DatabaseClient

load_dotenv()

print("=" * 80)
print("Schema Migration: is_returned INTEGER → BOOLEAN")
print("=" * 80)

# Build PostgreSQL connection
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT", "5432")

database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

print(f"\n📊 Connecting to: {postgres_host}:{postgres_port}/{postgres_db}")

try:
    db = DatabaseClient(database_url=database_url)
    print(f"✅ Connected successfully!")

    # Check current data
    counts = db.get_table_counts()
    print(f"\n📈 Current data in database:")
    for table, count in counts.items():
        print(f"   • {table}: {count} records")

    if counts['orders'] > 0:
        print(f"\n⚠️  WARNING: You have {counts['orders']} orders in the database.")
        print("This migration will clear all data and recreate the schema with proper types.")
        print("\nOptions:")
        print("1. Clear all data and recreate schema (RECOMMENDED)")
        print("2. Cancel and backup data first")

        choice = input("\nEnter choice (1/2): ").strip()

        if choice == "1":
            print("\n🗑️  Clearing all data...")
            db.clear_all_data()

            print("🔧 Dropping old tables...")
            db.drop_tables()

            print("✨ Creating new schema with BOOLEAN type...")
            db.create_tables()

            print("\n✅ Migration complete!")
            print("\nNext steps:")
            print("1. Run: python omnisupply_demo.py")
            print("2. Choose option 1 or 2 to reload your data")
            print("3. The is_returned column will now properly support boolean queries")
        else:
            print("\n❌ Migration cancelled. Please backup your data first.")
    else:
        print("\n📝 No data found. Recreating schema...")
        db.drop_tables()
        db.create_tables()
        print("✅ Schema updated successfully!")

    db.close()

except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
