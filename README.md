# OmniSupply: Multi-Agent Supply Chain Intelligence Platform

**Enterprise AI system for automated supply chain insights, risk predictions, and executive reporting.**

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-latest-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🎯 What is OmniSupply?

OmniSupply is a production-ready **multi-agent AI platform** that ingests real supply chain, sales, and financial data to provide:

- ✅ **Automated Insights**: AI-generated KPI summaries, trend analysis, anomaly detection
- ✅ **Risk Predictions**: Proactive alerts for delivery delays, inventory shortages, quality issues
- ✅ **Process Optimization**: Data-driven recommendations for cost reduction and efficiency
- ✅ **Executive Reporting**: Weekly/monthly CxO-level business intelligence reports
- ✅ **Workflow Automation**: Stakeholder alerts, task creation, meeting agendas

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
4. **Storage Layer**: DuckDB/PostgreSQL + ChromaDB for semantic search

[📖 Full Architecture Documentation](OMNISUPPLY_ARCHITECTURE.md)

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/yourusername/OmniSupply-AI-Multi-Agent-Supply-Chain-Intelligence-Platform.git
cd OmniSupply-AI-Multi-Agent-Supply-Chain-Intelligence-Platform

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Environment

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=duckdb:///data/omnisupply.db
OPIK_PROJECT_NAME=omnisupply
```

### 3. Prepare Data

Place your CSV files in the `data/` directory:

```
data/
├── retail_orders.csv
├── supply_chain.csv
├── inventory.csv
└── financial_data.csv
```

### 4. Run Complete Multi-Agent Demo

```bash
python omnisupply_demo.py
```

This will:
- Load and validate all datasets (~400K+ records)
- Store data in SQL database (DuckDB) and vector store (ChromaDB)
- Initialize all 5 specialized agents
- Test individual agent capabilities
- Demonstrate Supervisor multi-agent orchestration
- Generate executive reports with cross-agent insights

**Alternative**: Run the basic example:

```bash
python example_usage.py
```

---

## 📊 Datasets

The platform supports these data types:

### 1. Orders (`retail_orders.csv`)
- Order ID, date, customer segment
- Product category, sub-category, pricing
- Discounts, profit, returns
- **~222K records**

### 2. Shipments (`supply_chain.csv`)
- Shipment tracking, carrier, routes
- Expected vs actual delivery dates
- Freight costs, delays, reasons
- **~10K records**

### 3. Inventory (`inventory.csv`)
- SKU, product name, warehouse
- Stock levels, reorder points
- Lead times, supplier info
- **~5K SKUs**

### 4. Financial (`financial_data.csv`)
- Transactions (revenue, COGS, expenses)
- Categories, cost centers, vendors
- P&L components
- **~190K transactions**

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

### Phase 1: Core Platform ✅
- [x] Data ingestion pipeline
- [x] SQL + Vector storage
- [x] BaseAgent abstraction
- [x] Supervisor orchestration
- [x] Agent notebooks (5 agents)

### Phase 2: Production Agents (Next)
- [ ] Implement production agent classes
- [ ] SQL query generation (Data Analyst)
- [ ] Risk scoring models
- [ ] Prophet forecasting (Finance)

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
- [OpenAI](https://openai.com) - LLMs
- [ChromaDB](https://www.trychroma.com) - Vector search
- [DuckDB](https://duckdb.org) - Analytics database
- [Opik](https://www.comet.com/site/products/opik/) - LLM observability

---

## 📧 Contact

Questions or feedback? Open an issue or reach out to the team.

---

**⭐ If you find OmniSupply useful, please star the repository!**
