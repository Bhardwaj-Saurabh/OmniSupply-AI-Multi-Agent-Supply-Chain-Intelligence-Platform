# OmniSupply Multi-Agent Platform Architecture

**Enterprise AI system for supply chain intelligence, automated insights, and executive reporting.**

---

## Overview

OmniSupply is a production-ready multi-agent platform that ingests real supply chain, sales, and financial data to provide:

- **Automated Insights**: AI-generated KPI summaries and trend analysis
- **Risk Predictions**: Proactive alerts for delivery delays, inventory issues, quality problems
- **Process Optimization**: Data-driven recommendations for efficiency improvements
- **Executive Reporting**: Weekly/monthly CxO-level business intelligence
- **Workflow Automation**: Stakeholder alerts, task creation, meeting agendas

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Interface                              │
│  (API, CLI, Scheduled Jobs, Email Notifications)                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                      Supervisor Agent                                │
│  • Query understanding & task planning                               │
│  • Agent selection & routing                                         │
│  • Parallel/sequential execution                                     │
│  • Result aggregation & report generation                            │
└──────────┬─────────────┬──────────────┬─────────────┬───────────────┘
           │             │              │             │
    ┌──────▼──────┐ ┌───▼────┐  ┌─────▼──────┐ ┌────▼─────┐ ┌────▼────┐
    │ Data        │ │ Risk   │  │ Finance    │ │ Meeting  │ │ Email   │
    │ Analyst     │ │ Agent  │  │ Agent      │ │ Agent    │ │ Agent   │
    │ Agent       │ │        │  │            │ │          │ │         │
    │ • SQL       │ │ • Risk │  │ • P&L      │ │ • Reports│ │ • Alerts│
    │ • Viz       │ │ • Pred │  │ • Cashflow │ │ • CxO    │ │ • Tasks │
    │ • Anomaly   │ │ • Alert│  │ • Forecast │ │ • Actions│ │ • Agendas│
    └──────┬──────┘ └───┬────┘  └─────┬──────┘ └────┬─────┘ └────┬────┘
           │            │              │             │            │
           └────────────┴──────────────┴─────────────┴────────────┘
                                       │
                     ┌─────────────────▼──────────────────┐
                     │         Storage Layer               │
                     │                                     │
                     │  ┌──────────────┐  ┌─────────────┐ │
                     │  │ SQL Database │  │ Vector DB   │ │
                     │  │ (DuckDB/     │  │ (ChromaDB)  │ │
                     │  │  PostgreSQL) │  │             │ │
                     │  │              │  │ • Semantic  │ │
                     │  │ • Orders     │  │   Search    │ │
                     │  │ • Shipments  │  │ • Report    │ │
                     │  │ • Inventory  │  │   History   │ │
                     │  │ • Financials │  │ • Similar   │ │
                     │  │ • Logs       │  │   Patterns  │ │
                     │  └──────────────┘  └─────────────┘ │
                     └─────────────────────────────────────┘
                                       │
                     ┌─────────────────▼──────────────────┐
                     │      Data Ingestion Layer          │
                     │                                     │
                     │  • CSV Loaders                      │
                     │  • Data Validation                  │
                     │  • Quality Checks                   │
                     │  • Schema Normalization             │
                     └─────────────────────────────────────┘
```

---

## Core Components

### 1. Data Ingestion Pipeline (`src/data/ingestion/`)

**Purpose**: Load, validate, and normalize raw data

**Components**:
- **loaders.py**: CSV ingestion with encoding detection
  - `OrderLoader`: Retail orders
  - `ShipmentLoader`: Supply chain shipments
  - `InventoryLoader`: Stock levels
  - `FinancialLoader`: Transactions
  - `OmniSupplyDataLoader`: Master loader for all datasets

- **validators.py**: Data quality checks
  - Duplicate detection
  - Business rule validation
  - Anomaly detection
  - Statistical summaries

**Features**:
- Automatic encoding detection (UTF-8, Latin-1, etc.)
- Pydantic model validation
- Error handling and recovery
- Detailed logging

---

### 2. Storage Layer

#### SQL Database (`src/storage/sql/`)

**Purpose**: Structured data storage for analytics

**Technologies**:
- **DuckDB** (default): In-process analytics DB, perfect for OLAP queries
- **PostgreSQL**: Production-grade for multi-user deployments

**Tables**:
- `orders`: Retail sales data
- `shipments`: Supply chain logistics
- `inventory`: Stock levels
- `financial_transactions`: Revenue, expenses, COGS
- `agent_executions`: Execution logs (observability)
- `report_archive`: Historical reports
- `alert_log`: Alert history

**Features**:
- SQLAlchemy ORM models
- Bulk insert operations
- Indexed for performance
- Raw SQL query support

#### Vector Database (`src/storage/vector/`)

**Purpose**: Semantic search and pattern matching

**Technology**: ChromaDB with OpenAI embeddings

**Use Cases**:
- "Find similar orders to this one"
- "What reports did we generate about inventory last month?"
- "Show historical patterns for late deliveries"

**Features**:
- Text-to-vector conversion
- Similarity search
- Metadata filtering
- Document preprocessing

---

### 3. Agent Framework (`src/agents/`)

#### BaseAgent (`base.py`)

**Purpose**: Abstract base class for all agents

**Key Methods**:
- `execute(query, context)`: Main entry point
- `_build_graph()`: Define LangGraph workflow
- `get_capabilities()`: Return agent abilities
- `can_handle(query)`: Confidence scoring

**Features**:
- Standardized interface
- Opik observability integration
- Error handling
- Result formatting

#### Agent Registry

**Purpose**: Central registry for agent discovery

**Features**:
- Dynamic agent registration
- Capability listing
- Best agent selection
- Query routing

---

### 4. Supervisor Agent (`src/supervisor/`)

**Purpose**: Orchestrate multiple agents to fulfill complex queries

**Workflow**:

1. **Parse Query**: Understand user intent
2. **Plan Task**: Break into actionable steps
3. **Select Agents**: Choose relevant agents
4. **Execute**: Run agents (parallel or sequential)
5. **Aggregate**: Combine results
6. **Generate Report**: Create executive summary

**Key Features**:
- Parallel agent execution (async)
- Sequential execution with context passing
- LLM-powered routing decisions
- Executive report generation

**Structured Outputs**:
- `AgentSelection`: Which agents to invoke
- `TaskPlan`: Step-by-step execution plan
- `ExecutiveSummary`: Final report structure

---

## Data Flow

### Ingestion → Storage → Query → Insight

```
1. Raw CSV Files
   ↓
2. DataLoader (encoding detection, parsing)
   ↓
3. Pydantic Models (validation, type safety)
   ↓
4. DataValidator (quality checks)
   ↓
5. DatabaseClient (SQL insert)
   ↓
6. VectorStore (semantic indexing)
   ↓
7. Agent Query (SQL, semantic search)
   ↓
8. LLM Analysis (insights, recommendations)
   ↓
9. AgentResult (structured output)
   ↓
10. Supervisor (aggregation)
   ↓
11. Executive Report (markdown)
```

---

## Key Design Patterns

### 1. Pydantic Models for Type Safety

All data uses Pydantic models for validation:

```python
class Order(BaseModel):
    order_id: str
    order_date: datetime
    sale_price: Decimal
    profit: Decimal
    # ... with validators
```

### 2. LangGraph State Machines

Agents use LangGraph for workflow:

```python
workflow = StateGraph(AgentState)
workflow.add_node("parse", parse_node)
workflow.add_node("query", query_node)
workflow.add_node("analyze", analyze_node)
workflow.add_edge("parse", "query")
# ...
```

### 3. Structured LLM Outputs

Use `llm.with_structured_output(Model)` for type-safe LLM responses:

```python
llm_router = llm.with_structured_output(AgentSelection)
selection: AgentSelection = llm_router.invoke(prompt)
```

### 4. Observability with Opik

All agent executions are traced:

```python
@track(project_name="omnisupply")
def execute(self, query):
    # Opik automatically logs execution
```

---

## Technology Stack

### Core
- **Python 3.11+**
- **OpenAI GPT-4o-mini** (LLM)
- **LangGraph** (agent workflows)
- **Pydantic** (data validation)

### Storage
- **DuckDB** (analytics SQL)
- **PostgreSQL** (production SQL)
- **ChromaDB** (vector search)
- **SQLAlchemy** (ORM)

### Observability
- **Opik** (trace logging)
- **Python logging** (application logs)

### Future Additions
- **FastAPI** (REST API)
- **Celery** (task scheduling)
- **Redis** (task queue)

---

## Configuration

### Environment Variables (`.env`)

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Database
DATABASE_URL=duckdb:///data/omnisupply.db
# or for PostgreSQL:
# DATABASE_URL=postgresql://user:pass@host:5432/omnisupply

# Opik
OPIK_PROJECT_NAME=omnisupply

# Agent Settings
AGENT_TEMPERATURE=0.2
AGENT_MAX_TOKENS=4000

# API (future)
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Usage Example

```python
from src.data.ingestion.loaders import OmniSupplyDataLoader
from src.storage.sql.database import DatabaseClient
from src.agents.base import AgentRegistry
from src.supervisor.orchestrator import SupervisorAgent

# 1. Load data
loader = OmniSupplyDataLoader(data_dir="data")
data = loader.load_all()

# 2. Store in database
db = DatabaseClient()
db.load_all_data(data)

# 3. Register agents
registry = AgentRegistry()
registry.register(DataAnalystAgent(db=db))
registry.register(RiskAgent(db=db))
registry.register(FinanceAgent(db=db))

# 4. Create supervisor
supervisor = SupervisorAgent(agent_registry=registry)

# 5. Execute query
result = supervisor.execute(
    "What are the top 3 risks and generate a weekly report"
)

print(result['final_report'])
```

---

## Next Steps for Production

### Phase 1: Agent Implementation
- [ ] Implement DataAnalystAgent
- [ ] Implement RiskAgent
- [ ] Implement FinanceAgent
- [ ] Implement MeetingAgent
- [ ] Implement EmailAgent

### Phase 2: API Layer
- [ ] FastAPI endpoints
- [ ] Authentication
- [ ] Rate limiting

### Phase 3: Automation
- [ ] Celery task queue
- [ ] Scheduled reports
- [ ] Real-time monitoring

### Phase 4: Deployment
- [ ] Docker containers
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline
- [ ] Production monitoring

---

## Performance Considerations

### SQL Optimization
- Indexed columns for common queries
- Bulk insert operations
- Connection pooling

### Vector Search
- Batch embedding generation
- Metadata filtering
- Result caching

### Agent Execution
- Parallel agent execution (async)
- LLM response caching
- Token usage monitoring

### Scalability
- Stateless agents (horizontal scaling)
- Database connection pooling
- Task queue for async operations

---

## Security

- API key management (env vars, secrets)
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)
- Rate limiting (future)
- Authentication/authorization (future)

---

## Observability

### Opik Tracing
- Agent execution time
- Token usage
- Cost tracking
- Error rates

### Application Logs
- Structured logging
- Error tracking
- Audit trail

### Metrics (future)
- Query latency
- Agent success rates
- Cost per query
- User analytics

---

## Testing Strategy

### Unit Tests
- Data loaders
- Validators
- Database operations
- Agent logic

### Integration Tests
- End-to-end workflows
- Multi-agent orchestration
- Database interactions

### Performance Tests
- Load testing
- Query performance
- Concurrent users

---

## License

MIT License (or your chosen license)

---

## Contact

For questions or support, please contact the OmniSupply team.
