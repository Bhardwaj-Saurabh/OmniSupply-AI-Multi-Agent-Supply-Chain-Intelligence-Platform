"""
Quick demo with small dataset for fast testing
Loads only first 10,000 orders to avoid timeouts
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
from src.storage.vector.chromadb_client import OmniSupplyVectorStore
from src.agents import AgentRegistry, DataAnalystAgent, RiskAgent, FinanceAgent

print("="*80)
print("  🚀 OmniSupply Quick Demo (Small Dataset)")
print("="*80)
print("\nThis demo loads only 10,000 orders for fast testing\n")

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
print(f"📊 Connecting to PostgreSQL: {postgres_host}:{postgres_port}/{postgres_db}")

db = DatabaseClient(database_url=database_url)
print(f"✅ Connected!\n")

# Load small dataset
print("📥 Loading data (first 10,000 records only)...")
data_dir = Path("data")
loader = OmniSupplyDataLoader(data_dir=str(data_dir))
data = loader.load_all()

# Limit to first 10K
print(f"✅ Loaded from files:")
print(f"   • Orders: {len(data.get('orders', []))} records")
print(f"   • Limiting to first 10,000...")

data['orders'] = data['orders'][:10000] if 'orders' in data else []
data['transactions'] = data['transactions'][:20000] if 'transactions' in data else []

# Insert data
print("\n💾 Inserting into database...")
counts = db.load_all_data(data, clear_existing=False)

final_counts = db.get_table_counts()
print(f"\n✅ Database now contains:")
for table, count in final_counts.items():
    new = counts.get(table, 0)
    print(f"   • {table}: {count} total ({new} new)")

# Test agents
print("\n🤖 Initializing agents...")
registry = AgentRegistry()

data_analyst = DataAnalystAgent(db_client=db, vector_store=None)
registry.register(data_analyst)
print(f"✅ {data_analyst.name}")

risk_agent = RiskAgent(db_client=db, vector_store=None)
registry.register(risk_agent)
print(f"✅ {risk_agent.name}")

finance_agent = FinanceAgent(db_client=db, vector_store=None)
registry.register(finance_agent)
print(f"✅ {finance_agent.name}")

# Test Data Analyst
print("\n🧪 Testing Data Analyst Agent...")
try:
    result = data_analyst.execute("Show me total revenue by category")
    print(f"✅ Success: {result.success}")
    if result.insights:
        print(f"💡 Insights: {result.insights[0]}")
except Exception as e:
    print(f"❌ Error: {e}")

db.close()
print("\n✅ Quick demo complete!")
print(f"\n📊 Database Stats:")
print(f"   • Connection: {postgres_host}:{postgres_port}")
print(f"   • Schema: omnisupply")
print(f"   • Tables populated: {len([c for c in final_counts.values() if c > 0])}/4")
