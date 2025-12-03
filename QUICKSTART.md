# OmniSupply Quick Start Guide

Get up and running with OmniSupply in 10 minutes!

---

## Prerequisites

- Python 3.11 or higher
- OpenAI API key
- CSV data files (orders, shipments, inventory, financial)

---

## Step 1: Install Dependencies (2 min)

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

---

## Step 2: Configure Environment (1 min)

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional (these are defaults)
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=duckdb:///data/omnisupply.db
OPIK_PROJECT_NAME=omnisupply
```

Get your OpenAI API key from: https://platform.openai.com/api-keys

---

## Step 3: Prepare Data (2 min)

Place your CSV files in the `data/` directory:

```bash
mkdir -p data

# Copy your files:
# data/retail_orders.csv
# data/supply_chain.csv
# data/inventory.csv
# data/financial_data.csv
```

**Expected CSV formats**:

### retail_orders.csv
```
order_id,order_date,category,sale_price,profit,quantity,discount_percent,returned,...
```

### supply_chain.csv
```
shipment_id,carrier,shipment_date,expected_delivery,actual_delivery,status,...
```

### inventory.csv
```
sku,product_id,product_name,stock_quantity,reorder_level,warehouse_location,...
```

### financial_data.csv
```
transaction_id,transaction_date,transaction_type,category,amount,...
```

---

## Step 4: Run Demo (5 min)

```bash
python example_usage.py
```

This will:

1. ✅ Load all datasets (~400K+ records)
2. ✅ Validate data quality
3. ✅ Store in SQL database (DuckDB)
4. ✅ Index for semantic search (ChromaDB)
5. ✅ Show agent capabilities

**Expected output**:

```
🚀 OmniSupply Multi-Agent Platform Demo
================================================================================

📥 STEP 1: Loading datasets...
✅ Data loaded successfully:
  - Orders: 222,678
  - Shipments: 10,324
  - Inventory: 5,234
  - Transactions: 190,234

🔍 STEP 2: Validating data quality...
[Validation results...]

💾 STEP 3: Storing data in SQL database...
✅ Data stored in SQL:
  - orders: 222,678 records
  - shipments: 10,324 records
  ...

🔍 STEP 4: Indexing data for semantic search...
✅ Vector store ready: 200 documents indexed

🤖 STEP 5: Registering agents...
✅ Demo Complete!
```

---

## Step 5: Use the Platform

### Option A: Interactive Python

```python
from src.data.ingestion.loaders import OmniSupplyDataLoader
from src.storage.sql.database import DatabaseClient
from src.storage.vector.chromadb_client import OmniSupplyVectorStore

# Load data
loader = OmniSupplyDataLoader(data_dir="data")
data = loader.load_all()

# Store in database
db = DatabaseClient()
db.load_all_data(data)

# Query database
results = db.execute_query("SELECT category, SUM(sale_price) as revenue FROM orders GROUP BY category ORDER BY revenue DESC LIMIT 5")
for row in results:
    print(f"{row['category']}: ${row['revenue']:,.2f}")

# Semantic search
vector_store = OmniSupplyVectorStore()
results = vector_store.search_all("late deliveries", n_results=5)
for r in results:
    print(r['document'])
```

### Option B: Supervisor Agent (Future)

Once you implement agent classes:

```python
from src.agents.base import AgentRegistry
from src.supervisor.orchestrator import SupervisorAgent
from src.agents.data_analyst import DataAnalystAgent
from src.agents.risk_agent import RiskAgent

# Register agents
registry = AgentRegistry()
registry.register(DataAnalystAgent(db=db))
registry.register(RiskAgent(db=db))

# Create supervisor
supervisor = SupervisorAgent(agent_registry=registry)

# Execute query
result = supervisor.execute(
    "What are the top 3 supply chain risks this week?"
)

print(result['final_report'])
```

---

## Next Steps

### 1. Implement Production Agents

Convert your notebook agents to production classes:

```python
# src/agents/data_analyst.py
from .base import BaseAgent

class DataAnalystAgent(BaseAgent):
    def __init__(self, db, vector_store=None):
        super().__init__(
            name="data_analyst",
            db_client=db,
            vector_store=vector_store
        )

    def _build_graph(self):
        # Your LangGraph workflow from notebook
        pass

    def get_capabilities(self):
        return [
            "SQL query generation",
            "Data visualization",
            "Anomaly detection"
        ]
```

### 2. Test Agents

```python
# Test individual agent
agent = DataAnalystAgent(db=db)
result = agent.execute("Show top 10 products by revenue")
print(result.insights)
```

### 3. Deploy with API

Create a FastAPI server:

```python
# src/api/main.py
from fastapi import FastAPI
from src.supervisor import SupervisorAgent

app = FastAPI()
supervisor = SupervisorAgent(registry)

@app.post("/query")
def query(request: QueryRequest):
    result = supervisor.execute(request.query)
    return result
```

Run it:

```bash
uvicorn src.api.main:app --reload
```

### 4. Schedule Reports

```python
# Scheduled daily report
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=8, minute=0)
def daily_report():
    result = supervisor.execute("Generate daily executive summary")
    send_email(result['final_report'])

scheduler.start()
```

---

## Troubleshooting

### Issue: `FileNotFoundError` when loading data

**Solution**: Ensure CSV files are in `data/` directory:

```bash
ls -la data/
# Should show: retail_orders.csv, supply_chain.csv, etc.
```

### Issue: `OPENAI_API_KEY not found`

**Solution**: Create `.env` file with your API key:

```bash
echo "OPENAI_API_KEY=sk-your-key" > .env
```

### Issue: `UnicodeDecodeError` when loading CSV

**Solution**: The loader auto-detects encoding. If it still fails, convert your CSV to UTF-8:

```bash
iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv
```

### Issue: Database connection errors

**Solution**: DuckDB creates the file automatically. Ensure `data/` directory exists:

```bash
mkdir -p data
```

### Issue: ChromaDB errors

**Solution**: Install with pip:

```bash
pip install chromadb
```

---

## Performance Tips

### For Large Datasets (1M+ records)

1. **Use PostgreSQL instead of DuckDB**:
   ```bash
   DATABASE_URL=postgresql://user:pass@host:5432/omnisupply
   ```

2. **Batch vector indexing**:
   ```python
   # Index in batches
   vector_store.index_orders(orders[:1000])
   vector_store.index_orders(orders[1000:2000])
   ```

3. **Enable database connection pooling**:
   ```python
   db = DatabaseClient(
       database_url="postgresql://...",
       pool_size=10,
       max_overflow=20
   )
   ```

---

## Getting Help

- **Documentation**: See [OMNISUPPLY_ARCHITECTURE.md](OMNISUPPLY_ARCHITECTURE.md)
- **Examples**: Check `notebooks/` for agent implementations
- **Issues**: Open a GitHub issue

---

## What's Next?

You've completed the quickstart! Now you can:

1. ✅ Load and query your supply chain data
2. ✅ Run semantic searches
3. ✅ Validate data quality
4. 📝 Implement production agents (see notebooks for reference)
5. 🚀 Deploy with FastAPI
6. 📊 Schedule automated reports

**Happy building! 🎉**
