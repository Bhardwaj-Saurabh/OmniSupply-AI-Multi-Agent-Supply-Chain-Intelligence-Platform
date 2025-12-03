"""
Example usage of OmniSupply multi-agent platform.

This script demonstrates:
1. Data ingestion and validation
2. Storage in SQL + Vector DB
3. Agent registration
4. Supervisor orchestration
5. Executive report generation
"""

import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from src.data.ingestion.loaders import OmniSupplyDataLoader
from src.data.ingestion.validators import DataQualityChecker
from src.storage.sql.database import DatabaseClient
from src.storage.vector.chromadb_client import OmniSupplyVectorStore
from src.agents.base import AgentRegistry
from src.supervisor.orchestrator import SupervisorAgent


def main():
    """Main example workflow"""

    print("="*80)
    print("🚀 OmniSupply Multi-Agent Platform Demo")
    print("="*80)

    # ========================================================================
    # STEP 1: Data Ingestion
    # ========================================================================
    print("\n📥 STEP 1: Loading datasets...")

    data_loader = OmniSupplyDataLoader(data_dir="data")

    try:
        data = data_loader.load_all()

        print(f"\n✅ Data loaded successfully:")
        print(f"  - Orders: {len(data['orders']):,}")
        print(f"  - Shipments: {len(data['shipments']):,}")
        print(f"  - Inventory: {len(data['inventory']):,}")
        print(f"  - Transactions: {len(data['transactions']):,}")

    except FileNotFoundError as e:
        print(f"\n⚠️  Data files not found: {e}")
        print("   Please ensure CSV files are in the 'data/' directory")
        print("   Expected files:")
        print("     - data/retail_orders.csv")
        print("     - data/supply_chain.csv")
        print("     - data/inventory.csv")
        print("     - data/financial_data.csv")
        return

    # ========================================================================
    # STEP 2: Data Validation
    # ========================================================================
    print("\n🔍 STEP 2: Validating data quality...")

    quality_checker = DataQualityChecker()
    validation_results = quality_checker.check_all(data)
    quality_checker.print_summary(validation_results)

    # ========================================================================
    # STEP 3: SQL Storage
    # ========================================================================
    print("\n💾 STEP 3: Storing data in SQL database...")

    db_client = DatabaseClient(database_url="duckdb:///data/omnisupply.db")

    # Clear existing data (for demo)
    print("  Clearing existing data...")
    db_client.clear_all_data()

    # Insert data
    counts = db_client.load_all_data(data)

    print(f"\n✅ Data stored in SQL:")
    for table, count in counts.items():
        print(f"  - {table}: {count:,} records")

    # Verify
    table_counts = db_client.get_table_counts()
    print(f"\n📊 Database verification:")
    for table, count in table_counts.items():
        print(f"  - {table}: {count:,} records")

    # ========================================================================
    # STEP 4: Vector Store (Semantic Search)
    # ========================================================================
    print("\n🔍 STEP 4: Indexing data for semantic search...")

    vector_store = OmniSupplyVectorStore(persist_directory="data/chroma")

    # Reset for demo
    print("  Resetting vector store...")
    vector_store.store.reset()

    # Index data (use first 100 records for demo speed)
    print("  Indexing orders...")
    order_dicts = [o.model_dump() for o in data['orders'][:100]]
    vector_store.index_orders(order_dicts)

    print("  Indexing shipments...")
    shipment_dicts = [s.model_dump() for s in data['shipments'][:100]]
    vector_store.index_shipments(shipment_dicts)

    stats = vector_store.get_stats()
    print(f"\n✅ Vector store ready: {stats['total_documents']} documents indexed")

    # ========================================================================
    # STEP 5: Agent Registration
    # ========================================================================
    print("\n🤖 STEP 5: Registering agents...")

    registry = AgentRegistry()

    # Note: In a real implementation, you would import and register
    # actual agent implementations here. For this demo, we'll show
    # how the registry would work:

    print("\n  📝 Agent Registry:")
    print("     To use the platform, you would register agents like:")
    print("       registry.register(DataAnalystAgent(db=db_client, vector_store=vector_store))")
    print("       registry.register(RiskAgent(db=db_client))")
    print("       registry.register(FinanceAgent(db=db_client))")
    print("       registry.register(MeetingAgent())")
    print("       registry.register(EmailAgent())")

    print(f"\n  Currently registered: {len(registry)} agents")

    # ========================================================================
    # STEP 6: Supervisor Agent (Mock Example)
    # ========================================================================
    print("\n🎯 STEP 6: Supervisor Agent Demo...")

    if len(registry) > 0:
        supervisor = SupervisorAgent(agent_registry=registry)

        # Example query
        example_query = "Show me top risks and financial performance this week"

        print(f"\n  Query: '{example_query}'")
        print("\n  Supervisor workflow:")
        print("    1. Parse query")
        print("    2. Plan task (break into steps)")
        print("    3. Select agents (risk_agent, finance_agent)")
        print("    4. Execute agents (parallel)")
        print("    5. Aggregate results")
        print("    6. Generate executive report")

        # Execute (would work with registered agents)
        # result = supervisor.execute(example_query)
        # print(result['final_report'])

    else:
        print("\n  ⚠️  No agents registered. In production:")
        print("     - Create agent implementations (inherit from BaseAgent)")
        print("     - Register them with AgentRegistry")
        print("     - Supervisor will orchestrate them automatically")

    # ========================================================================
    # STEP 7: Example Queries
    # ========================================================================
    print("\n💡 STEP 7: Example queries you could run...")

    example_queries = [
        "What are the top 3 supply chain risks this month?",
        "Generate a weekly executive report with KPIs",
        "Which products have critical inventory levels?",
        "Show P&L summary and cashflow forecast",
        "Send alerts for late deliveries to operations team",
        "Prepare materials for Monday leadership meeting"
    ]

    print("\n  Example queries for the OmniSupply platform:")
    for i, query in enumerate(example_queries, 1):
        print(f"    {i}. {query}")

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "="*80)
    print("✅ Demo Complete!")
    print("="*80)

    print("\n📦 What was created:")
    print(f"  - SQL Database: data/omnisupply.db ({sum(table_counts.values()):,} records)")
    print(f"  - Vector Store: data/chroma ({stats['total_documents']} documents)")
    print(f"  - Agent Registry: {len(registry)} agents")

    print("\n🎯 Next Steps:")
    print("  1. Implement agent classes in src/agents/")
    print("     - data_analyst.py")
    print("     - risk_agent.py")
    print("     - finance_agent.py")
    print("     - meeting_agent.py")
    print("     - email_agent.py")
    print()
    print("  2. Register agents in your application:")
    print("     registry.register(YourAgent(db=db_client, vector_store=vector_store))")
    print()
    print("  3. Use Supervisor for orchestration:")
    print("     supervisor = SupervisorAgent(registry)")
    print("     result = supervisor.execute('your query here')")
    print()
    print("  4. Deploy with FastAPI (see src/api/)")
    print("  5. Schedule automated reports (see src/scheduler/)")

    print("\n" + "="*80)

    # Close connections
    db_client.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
