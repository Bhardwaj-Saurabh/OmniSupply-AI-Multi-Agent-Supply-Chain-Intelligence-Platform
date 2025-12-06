# OmniSupply: Multi-Agent Supply Chain Intelligence Platform

**Enterprise AI system for automated supply chain insights, risk predictions, and executive reporting.**

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-latest-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🎯 What is OmniSupply?

OmniSupply is a **production-ready multi-agent AI platform** that ingests real supply chain, sales, and financial data to provide:

- ✅ **Automated Insights**: AI-generated KPI summaries, trend analysis, anomaly detection
- ✅ **Risk Predictions**: Proactive alerts for delivery delays, inventory shortages, quality issues
- ✅ **Process Optimization**: Data-driven recommendations for cost reduction and efficiency
- ✅ **Executive Reporting**: Weekly/monthly CxO-level business intelligence reports
- ✅ **Workflow Automation**: Stakeholder alerts, task creation, meeting agendas

**Current Status**: ✅ **Fully Operational** with 416,962 records loaded across 4 data tables!

---

## 🏗️ Architecture

```
User Query → Supervisor Agent → [Data Analyst, Risk, Finance, Meeting, Email Agents]
                ↓
          Aggregation & Report Generation
                ↓
          Executive Summary + Actions
```

**Key Components**:
1. **Data Pipeline**: Ingestion, validation, storage (SQL + Vector DB)
2. **Specialized Agents**: Domain experts (data, risk, finance, reporting, workflow)
3. **Supervisor Agent**: Orchestrates agents, aggregates results, generates reports
4. **Storage Layer**: PostgreSQL + ChromaDB for semantic search

[📖 Full Architecture Documentation](OMNISUPPLY_ARCHITECTURE.md)

---

## 🚀 Quick Start

### 1. Installation

This project uses **[uv](https://github.com/astral-sh/uv)** for fast, reliable Python package management.

```bash
# Clone repository
git clone https://github.com/yourusername/OmniSupply-AI-Multi-Agent-Supply-Chain-Intelligence-Platform.git
cd OmniSupply-AI-Multi-Agent-Supply-Chain-Intelligence-Platform

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# This will:
# - Create .venv/ if it doesn't exist
# - Install all dependencies from pyproject.toml
# - Lock versions in uv.lock
```

**Alternative (traditional pip)**:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup PostgreSQL Database

**Option A: Local PostgreSQL (Recommended)**

Run the setup script to create a local PostgreSQL instance via Docker:

```bash
bash setup_local_postgres.sh
```

This will:
- Create a PostgreSQL 15 Docker container
- Configure database: `omnisupply`
- Setup user credentials
- Expose on port 5432

**Option B: Remote PostgreSQL**

If you have an existing PostgreSQL server, skip the script and configure your connection in `.env`

### 3. Setup Environment

Create a `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# PostgreSQL Configuration (Local Docker)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=omnisupply
POSTGRES_PASSWORD=omnisupply123
POSTGRES_DB=omnisupply

# Observability
OPIK_PROJECT_NAME=omnisupply
```

### 4. Prepare Data

Place your CSV files in the `data/` directory:

```
data/
├── retail_orders.csv         # DataCo SMART SUPPLY CHAIN dataset
├── supply_chain.csv          # (optional)
├── inventory.csv             # (optional)
└── financial_data.csv        # (optional)
```

### 5. Load Data into PostgreSQL

```bash
# Load full dataset (180K orders + 351K transactions)
python load_full_data.py

# OR load small dataset for quick testing (10K orders)
python quick_demo_small_data.py
```

### 6. Run Complete Multi-Agent Demo

```bash
# Default: Auto-detect and use existing data (no prompts)
python omnisupply_demo.py

# Force reload: Clear and reload all data from CSV
python omnisupply_demo.py --reload

# Skip data loading: Use existing database only
python omnisupply_demo.py --skip-data
```

This will:
- ✅ Automatically detect and use existing data (no manual prompts)
- ✅ Validate database connection (416,962 records loaded)
- ✅ Initialize all 5 specialized agents
- ✅ Test individual agent capabilities
- ✅ Demonstrate Supervisor multi-agent orchestration
- ✅ Generate executive reports with cross-agent insights

**Example Output**:
```
📊 Connecting to PostgreSQL: localhost:5432/omnisupply
✅ Connected to PostgreSQL successfully!
✅ Database already contains 65,952 records:
   • orders: 65,752 records
   • shipments: 100 records

📊 Using existing data (no reload needed)

🤖 STEP 2: Initializing Agents
✅ data_analyst: SQL query generation, trend analysis
✅ risk_agent: Risk assessment, delivery/inventory alerts
✅ finance_agent: P&L reports, cashflow forecasting
✅ meeting_agent: Executive summaries, weekly reports
✅ email_agent: Stakeholder alerts, task automation
```

---

## 📊 Datasets

The platform currently has **416,962 records loaded** across 4 tables:

### 1. Orders (`retail_orders.csv`)
- Order ID, date, customer segment, region
- Product category, sub-category, pricing
- Discounts, profit, returns, shipping details
- **65,752 records** (deduplicated from 180K raw records)
- Source: DataCo SMART SUPPLY CHAIN dataset

### 2. Financial Transactions (`financial_data.csv`)
- Transaction types (revenue, COGS, expenses, discounts)
- Categories, cost centers, business units
- P&L components, vendor information
- **351,010 records**

### 3. Shipments (`supply_chain.csv`)
- Shipment tracking, carrier, routes
- Expected vs actual delivery dates
- Freight costs, delays, late delivery tracking
- **100 records** (sample data)

### 4. Inventory (`inventory.csv`)
- SKU, product name, warehouse location
- Stock levels, reorder points, reorder quantities
- Lead times, supplier information, unit costs
- **100 records** (sample data)

---

## 🤖 Agent Capabilities

### 1. Data Analyst Agent
- SQL query generation
- Data visualization
- Anomaly detection
- Trend analysis

### 2. Supply Chain Risk Agent
- Multi-dimensional risk scoring
- Late delivery prediction
- Inventory shortage alerts
- Quality issue detection

### 3. Finance Insight Agent
- P&L summarization
- Expense analysis
- Cashflow forecasting (Prophet)
- Budget variance

### 4. Meeting/Report Agent
- Weekly/monthly reports
- CxO executive summaries
- Top 3 recommended actions
- KPI dashboards

### 5. Email/Workflow Agent
- Stakeholder alerts
- Task creation
- Meeting agenda generation
- Follow-up automation

---

## 💡 Example Queries

```python
from src.supervisor.orchestrator import SupervisorAgent

supervisor = SupervisorAgent(agent_registry=registry)

# Example 1: Risk analysis
result = supervisor.execute(
    "What are the top 3 supply chain risks this month?"
)

# Example 2: Executive report
result = supervisor.execute(
    "Generate weekly executive summary with KPIs and recommendations"
)

# Example 3: Financial analysis
result = supervisor.execute(
    "Show P&L summary and forecast next 90 days cashflow"
)

# Example 4: Inventory alerts
result = supervisor.execute(
    "Which products are at critical stock levels? Send alerts to operations."
)

print(result['final_report'])
```

---

## 🛠️ Project Structure

```
OmniSupply/
├── src/
│   ├── data/
│   │   ├── models.py              # Pydantic data models
│   │   └── ingestion/
│   │       ├── loaders.py         # CSV loaders
│   │       └── validators.py      # Data quality checks
│   ├── storage/
│   │   ├── sql/
│   │   │   ├── models.py          # SQLAlchemy ORM
│   │   │   └── database.py        # DB client
│   │   └── vector/
│   │       ├── embeddings.py      # Text → vectors
│   │       └── chromadb_client.py # Vector store
│   ├── agents/
│   │   └── base.py                # BaseAgent abstraction
│   └── supervisor/
│       └── orchestrator.py        # Supervisor agent
├── notebooks/
│   ├── data_analyst_agent_enhanced.ipynb
│   ├── supply_chain_risk_agent.ipynb
│   ├── finance_insight_agent.ipynb
│   ├── meeting_report_agent.ipynb
│   └── email_workflow_agent.ipynb
├── config/
│   └── settings.py                # Configuration
├── data/                          # Your CSV files here
├── example_usage.py               # Demo script
├── requirements.txt
└── README.md
```

---

## 📈 Features

### Data Pipeline
- ✅ Automatic encoding detection
- ✅ Pydantic validation
- ✅ Data quality checks
- ✅ Business rule validation

### Storage
- ✅ SQL (DuckDB/PostgreSQL)
- ✅ Vector DB (ChromaDB + OpenAI embeddings)
- ✅ Bulk operations
- ✅ Semantic search

### Agent Framework
- ✅ BaseAgent abstraction
- ✅ LangGraph workflows
- ✅ Structured LLM outputs (Pydantic)
- ✅ Opik observability

### Supervisor
- ✅ Intelligent query routing
- ✅ Task planning
- ✅ Parallel agent execution
- ✅ Result aggregation
- ✅ Executive report generation

---

## 🔮 Roadmap

### Phase 1: Core Platform ✅ **COMPLETED**
- [x] Data ingestion pipeline with validation
- [x] PostgreSQL + ChromaDB storage
- [x] BaseAgent abstraction
- [x] Supervisor orchestration with LangGraph
- [x] Agent notebooks (5 agents)

### Phase 2: Production Agents ✅ **COMPLETED**
- [x] Implement production agent classes (5 agents)
- [x] SQL query generation (Data Analyst)
- [x] Risk scoring models (Risk Agent)
- [x] P&L reporting (Finance Agent)
- [x] Executive report generation (Meeting Agent)
- [x] Alert workflow automation (Email Agent)
- [x] Local PostgreSQL setup via Docker
- [x] Full dataset loaded (416K+ records)

### Phase 3: API Layer
- [ ] FastAPI endpoints
- [ ] Authentication
- [ ] Rate limiting
- [ ] API documentation

### Phase 4: Automation
- [ ] Celery task queue
- [ ] Scheduled reports
- [ ] Real-time monitoring
- [ ] Email integration

### Phase 5: Deployment
- [ ] Docker containers
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline
- [ ] Cloud deployment

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_data_loader.py
```

---

## 📚 Documentation

- [Architecture Overview](OMNISUPPLY_ARCHITECTURE.md) - Detailed system design
- [Agent Plans](notebooks/) - Individual agent implementations
- [API Documentation](#) - Coming soon

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent workflows
- [OpenAI](https://openai.com) - LLMs (GPT-4o-mini)
- [ChromaDB](https://www.trychroma.com) - Vector search
- [PostgreSQL](https://www.postgresql.org) - Production database
- [Opik](https://www.comet.com/site/products/opik/) - LLM observability
- [Docker](https://www.docker.com) - Local PostgreSQL containerization

---

## 📧 Contact

Questions or feedback? Open an issue or reach out to the team.

---

**⭐ If you find OmniSupply useful, please star the repository!**
