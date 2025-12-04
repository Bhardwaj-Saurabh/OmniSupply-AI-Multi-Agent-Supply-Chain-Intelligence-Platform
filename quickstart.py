"""
Quick start demo - runs automatically without prompts.
Loads data fresh into PostgreSQL and runs example queries.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

from src.storage.sql.database import DatabaseClient
from src.data.ingestion.loaders import OmniSupplyDataLoader
from src.data.ingestion.validators import DataQualityChecker

load_dotenv()

print("=" * 80)
print("  OmniSupply Quick Start")
print("=" * 80)

# Connect to PostgreSQL
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT", "5432")

database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

print(f"\n📊 Connecting to PostgreSQL...")
db = DatabaseClient(database_url=database_url)
print(f"✅ Connected!")

# Check existing data
counts = db.get_table_counts()
print(f"\n📈 Current database state:")
for table, count in counts.items():
    print(f"   • {table}: {count} records")

if db.has_data():
    print("\n🗑️  Clearing existing data...")
    db.clear_all_data()
    print("✅ Data cleared!")

# Load fresh data
print("\n📥 Loading data from CSV files...")
data_dir = Path("data")
loader = OmniSupplyDataLoader(data_dir=str(data_dir))
data = loader.load_all()

print(f"✅ Loaded:")
print(f"   • Orders: {len(data.get('orders', []))} records")
print(f"   • Shipments: {len(data.get('shipments', []))} records")
print(f"   • Inventory: {len(data.get('inventory', []))} records")
print(f"   • Transactions: {len(data.get('transactions', []))} records")

# Validate
print("\n🔍 Validating data...")
checker = DataQualityChecker()
validation_results = checker.check_all(data)

for dataset_name, result in validation_results.items():
    status_icon = "✅" if result.status == "PASSED" else "❌"
    print(f"   {status_icon} {dataset_name}: {result.status}")

# Insert into database
print("\n💾 Inserting into database...")
inserted_counts = db.load_all_data(data, clear_existing=False)

final_counts = db.get_table_counts()
print(f"\n✅ Database populated:")
for table, count in final_counts.items():
    new = inserted_counts.get(table, 0)
    print(f"   • {table}: {count} total ({new} new)")

# Run sample query
print("\n🧪 Running sample query...")
query = "SELECT COUNT(*) as total FROM orders"
result = db.execute_query(query)
print(f"Total orders: {result[0]['total']}")

db.close()
print("\n✅ Quick start complete!")
print("\nNext step: Run 'python omnisupply_demo.py' for full agent demo")
