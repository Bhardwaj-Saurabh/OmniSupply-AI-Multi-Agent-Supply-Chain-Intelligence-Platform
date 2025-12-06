"""
Load full dataset into PostgreSQL (all 180K orders)
Runs non-interactively with clear_existing=True
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("❌ ERROR: OPENAI_API_KEY not found")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))

from src.data.ingestion.loaders import OmniSupplyDataLoader
from src.storage.sql.database import DatabaseClient

print("="*80)
print("  📥 OmniSupply - Load Full Dataset")
print("="*80)

# PostgreSQL connection
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT", "5432")

if not all([postgres_host, postgres_user, postgres_password, postgres_db]):
    print("❌ ERROR: PostgreSQL configuration incomplete")
    sys.exit(1)

database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
print(f"\n📊 Connecting to PostgreSQL: {postgres_host}:{postgres_port}/{postgres_db}")

db = DatabaseClient(database_url=database_url)
print(f"✅ Connected!\n")

# Load full dataset
print("📥 Loading FULL dataset (all records)...")
data_dir = Path("data")
loader = OmniSupplyDataLoader(data_dir=str(data_dir))
data = loader.load_all()

print(f"\n✅ Loaded from files:")
print(f"   • Orders: {len(data.get('orders', []))} records")
print(f"   • Shipments: {len(data.get('shipments', []))} records")
print(f"   • Inventory: {len(data.get('inventory', []))} records")
print(f"   • Transactions: {len(data.get('transactions', []))} records")

# Insert data (clear existing and load fresh)
print(f"\n💾 Clearing existing data and inserting full dataset...")
print(f"⏳ This may take 2-3 minutes for 180K+ orders...")

counts = db.load_all_data(data, clear_existing=True)

final_counts = db.get_table_counts()
print(f"\n✅ Database now contains:")
for table, count in final_counts.items():
    new = counts.get(table, 0)
    print(f"   • {table}: {count:,} total ({new:,} new)")

db.close()
print("\n✅ Full dataset loaded successfully!")
print(f"\n📊 Database Stats:")
print(f"   • Connection: {postgres_host}:{postgres_port}")
print(f"   • Database: {postgres_db}")
print(f"   • Total records: {sum(final_counts.values()):,}")
