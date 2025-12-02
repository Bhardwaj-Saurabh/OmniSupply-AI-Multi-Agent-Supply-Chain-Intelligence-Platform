# Data Analyst Agent Implementation Plan with LangGraph

## Project Overview
Building a Data Analyst Agent as the foundation agent for the OmniSupply AI Multi-Agent Supply Chain Intelligence Platform. This agent will analyze supply chain data, identify trends/outliers/anomalies, execute SQL queries, and auto-generate visualizations.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Analyst Agent                        │
│                     (LangGraph State Machine)                │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Query Parser │    │ SQL Executor │    │ Visualizer   │
│    Node      │    │     Node     │    │    Node      │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │  Anomaly Detector│
                    │      Node        │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Response        │
                    │  Generator Node  │
                    └──────────────────┘
```

---

## Phase 1: Project Setup & Dependencies

### 1.1 Directory Structure
```
omnisupply-ai/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── data_analyst/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py           # Main LangGraph agent
│   │   │   ├── graph.py           # Graph definition
│   │   │   ├── state.py           # State schema
│   │   │   ├── nodes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── query_parser.py
│   │   │   │   ├── sql_executor.py
│   │   │   │   ├── anomaly_detector.py
│   │   │   │   ├── visualizer.py
│   │   │   │   └── response_generator.py
│   │   │   └── tools/
│   │   │       ├── __init__.py
│   │   │       ├── sql_tool.py
│   │   │       ├── stats_tool.py
│   │   │       └── chart_tool.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py              # Data loading utilities
│   │   ├── processor.py           # Data cleaning/preprocessing
│   │   └── db_manager.py          # Database operations
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Configuration management
│   └── utils/
│       ├── __init__.py
│       ├── logger.py              # Logging utilities
│       └── prompts.py             # LLM prompts
├── tests/
│   ├── __init__.py
│   └── test_data_analyst.py
├── data/                          # Raw data files (existing)
├── notebooks/                     # Jupyter notebooks (existing)
├── .env                          # Environment variables
├── pyproject.toml                # Dependencies (existing)
└── README.md
```

### 1.2 Additional Dependencies
```toml
# Add to pyproject.toml
dependencies = [
    "langchain>=1.1.0",
    "langgraph>=1.0.4",
    "openai>=2.8.1",
    "openpyxl>=3.1.5",
    "pandas>=2.3.3",
    "pydantic>=2.12.5",
    "python-dotenv>=1.2.1",
    # New additions:
    "duckdb>=1.0.0",              # For SQL queries on DataFrames
    "plotly>=5.24.0",             # Interactive visualizations
    "scikit-learn>=1.5.0",        # Anomaly detection
    "langchain-openai>=0.3.0",    # OpenAI integration
    "opik>=0.2.0",                # Observability and evaluation (Comet)
    "chromadb>=0.6.0",            # Vector store for knowledge base
    "tiktoken>=0.9.0",            # Token counting
]
```

### 1.3 Environment Setup
```bash
# .env file
OPENAI_API_KEY=your-api-key-here
COMET_API_KEY=your-comet-api-key
COMET_WORKSPACE=your-workspace-name
OPIK_PROJECT_NAME=omnisupply-data-analyst
```

---

## Phase 2: Data Preparation Layer

### 2.1 Database Setup (DuckDB)
**File**: `src/data/db_manager.py`

**Purpose**: Convert CSV/Excel files into queryable SQL database

**Key Features**:
- Load all 4 datasets into DuckDB in-memory database
- Create indexes on key columns (dates, IDs, categories)
- Provide SQL query interface
- Handle encoding issues automatically

**Implementation**:
```python
class SupplyChainDBManager:
    def __init__(self, data_dir: str):
        self.conn = duckdb.connect(':memory:')
        self.load_all_datasets(data_dir)

    def load_all_datasets(self, data_dir: str):
        # Load DataCo Supply Chain
        # Load Dynamic Logistics
        # Load Retail Sales
        # Load Supply Chain Data

    def execute_query(self, query: str) -> pd.DataFrame:
        # Safe SQL execution with validation

    def get_schema(self) -> dict:
        # Return table schemas for LLM context
```

### 2.2 Data Loader & Preprocessor
**File**: `src/data/loader.py` & `src/data/processor.py`

**Purpose**: Load and clean data with proper encoding handling

**Key Features**:
- Auto-detect encoding (utf-8, latin-1, etc.)
- Handle missing values
- Parse dates
- Create derived features (e.g., delivery delay = actual - scheduled)
- Generate summary statistics

---

## Phase 3: LangGraph Agent Core

### 3.1 State Schema
**File**: `src/agents/data_analyst/state.py`

**Purpose**: Define the agent's state that flows through the graph

```python
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage

class DataAnalystState(TypedDict):
    """State for Data Analyst Agent"""
    # Input
    user_query: str
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]

    # Query Analysis
    query_type: Optional[str]  # 'trend', 'anomaly', 'sql', 'visualization'
    intent: Optional[str]      # Parsed intent

    # SQL Execution
    sql_query: Optional[str]
    query_results: Optional[pd.DataFrame]

    # Analysis
    insights: List[str]
    anomalies: List[dict]
    trends: List[dict]

    # Visualization
    charts: List[dict]  # Chart specifications

    # Output
    final_response: Optional[str]
    error: Optional[str]
```

### 3.2 Graph Nodes

#### Node 1: Query Parser
**File**: `src/agents/data_analyst/nodes/query_parser.py`

**Purpose**: Understand user intent and determine routing

**Input**: `user_query`
**Output**: `query_type`, `intent`

**Logic**:
- Use LLM to classify query type:
  - "Show me sales trends" → `trend`
  - "Detect anomalies in delivery" → `anomaly`
  - "What's the average profit by region?" → `sql`
  - "Chart monthly revenue" → `visualization`
- Extract key entities (date ranges, metrics, dimensions)

#### Node 2: SQL Executor
**File**: `src/agents/data_analyst/nodes/sql_executor.py`

**Purpose**: Convert natural language to SQL and execute

**Input**: `intent`, `query_type`
**Output**: `sql_query`, `query_results`

**Logic**:
- Use LLM with database schema to generate SQL
- Validate SQL for safety
- Execute on DuckDB
- Return results as DataFrame

**Example Prompt**:
```
You are a SQL expert. Given this database schema:
{schema}

Convert this user query to SQL:
"{user_query}"

Return only valid SQL, no explanations.
```

#### Node 3: Anomaly Detector
**File**: `src/agents/data_analyst/nodes/anomaly_detector.py`

**Purpose**: Detect statistical anomalies in data

**Input**: `query_results`
**Output**: `anomalies`

**Logic**:
- Use Isolation Forest or Z-score for numeric anomalies
- Detect late deliveries (actual > scheduled + threshold)
- Flag unusual spikes/drops in sales
- Identify inventory stockouts

#### Node 4: Visualizer
**File**: `src/agents/data_analyst/nodes/visualizer.py`

**Purpose**: Auto-generate charts based on data

**Input**: `query_results`, `query_type`
**Output**: `charts`

**Logic**:
- Time-series → Line chart
- Categorical comparison → Bar chart
- Distribution → Histogram
- Correlation → Scatter plot
- Use Plotly for interactive charts
- Return chart specs (JSON) that can be rendered

#### Node 5: Response Generator
**File**: `src/agents/data_analyst/nodes/response_generator.py`

**Purpose**: Generate human-readable insights

**Input**: `insights`, `anomalies`, `trends`, `charts`
**Output**: `final_response`

**Logic**:
- Use LLM to synthesize findings into narrative
- Include key metrics, trends, and recommendations
- Format with markdown for readability

### 3.3 Graph Definition
**File**: `src/agents/data_analyst/graph.py`

**Purpose**: Define the LangGraph workflow

```python
from langgraph.graph import StateGraph, END

def create_data_analyst_graph():
    workflow = StateGraph(DataAnalystState)

    # Add nodes
    workflow.add_node("parse_query", parse_query_node)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("detect_anomalies", detect_anomalies_node)
    workflow.add_node("visualize", visualize_node)
    workflow.add_node("generate_response", generate_response_node)

    # Define edges (routing logic)
    workflow.set_entry_point("parse_query")

    # Conditional routing based on query_type
    workflow.add_conditional_edges(
        "parse_query",
        route_query,
        {
            "sql": "execute_sql",
            "anomaly": "detect_anomalies",
            "visualization": "visualize",
            "trend": "execute_sql"
        }
    )

    # All paths converge to response generator
    workflow.add_edge("execute_sql", "generate_response")
    workflow.add_edge("detect_anomalies", "generate_response")
    workflow.add_edge("visualize", "generate_response")
    workflow.add_edge("generate_response", END)

    return workflow.compile()
```

### 3.4 Main Agent
**File**: `src/agents/data_analyst/agent.py`

**Purpose**: High-level agent interface

```python
class DataAnalystAgent:
    def __init__(self, db_manager: SupplyChainDBManager):
        self.db = db_manager
        self.graph = create_data_analyst_graph()

    def analyze(self, query: str) -> dict:
        """Main entry point for analysis"""
        initial_state = {
            "user_query": query,
            "messages": [],
            "insights": [],
            "anomalies": [],
            "trends": [],
            "charts": []
        }

        result = self.graph.invoke(initial_state)
        return result
```

---

## Phase 4: Tools Implementation

### 4.1 SQL Tool
**File**: `src/agents/data_analyst/tools/sql_tool.py`

```python
from langchain.tools import tool

@tool
def execute_sql_query(query: str, db_manager) -> dict:
    """Execute SQL query on supply chain database"""
    # Validate and sanitize SQL
    # Execute query
    # Return results with metadata
```

### 4.2 Statistics Tool
**File**: `src/agents/data_analyst/tools/stats_tool.py`

```python
@tool
def calculate_statistics(data: pd.DataFrame, column: str) -> dict:
    """Calculate descriptive statistics"""
    # Mean, median, std, quartiles
    # Detect outliers (Z-score > 3)
    # Return summary dict
```

### 4.3 Chart Tool
**File**: `src/agents/data_analyst/tools/chart_tool.py`

```python
@tool
def create_chart(data: pd.DataFrame, chart_type: str, x: str, y: str) -> dict:
    """Generate Plotly chart specification"""
    # Create appropriate chart
    # Return JSON spec that can be rendered
```

---

## Phase 5: Prompts & Configuration

### 5.1 Prompt Templates
**File**: `src/utils/prompts.py`

```python
QUERY_PARSER_PROMPT = """
You are a data analyst assistant for a supply chain platform.

User Query: {user_query}

Available datasets:
- DataCo Supply Chain (180K orders, shipping, customers)
- Dynamic Logistics (32K records, GPS, inventory, risk)
- Retail Sales (10K orders, profit, returns)
- Supply Chain Data (100 records, manufacturing)

Classify this query into ONE of these types:
1. 'sql' - Needs database query (e.g., "What's average sales by region?")
2. 'anomaly' - Needs anomaly detection (e.g., "Find unusual deliveries")
3. 'trend' - Needs trend analysis (e.g., "Show sales over time")
4. 'visualization' - Needs specific chart (e.g., "Plot profit by category")

Return JSON:
{{
  "query_type": "<type>",
  "intent": "<brief description>",
  "entities": {{
    "metrics": ["sales", "profit"],
    "dimensions": ["region", "category"],
    "date_range": "last 30 days"
  }}
}}
"""

SQL_GENERATOR_PROMPT = """
You are a SQL expert for a supply chain database.

Database Schema:
{schema}

User wants: {intent}

Generate a valid DuckDB SQL query. Rules:
1. Use only tables in the schema
2. Always use LIMIT 1000 for safety
3. Use clear column aliases
4. Return ONLY the SQL query, no explanation

SQL Query:
"""

INSIGHT_GENERATOR_PROMPT = """
You are a data analyst generating insights from supply chain data.

Query Results:
{results}

Anomalies Detected:
{anomalies}

Generate a concise analysis report:
1. Key Findings (2-3 bullet points)
2. Notable Trends or Patterns
3. Recommended Actions (if applicable)

Use markdown formatting. Be specific with numbers.
"""
```

### 5.2 Configuration
**File**: `src/config/settings.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.1

    # Data
    data_dir: str = "data"

    # Anomaly Detection
    anomaly_threshold: float = 3.0  # Z-score

    # Visualization
    chart_width: int = 800
    chart_height: int = 500

    class Config:
        env_file = ".env"
```

---

## Phase 6: Testing & Examples

### 6.1 Test Cases
**File**: `tests/test_data_analyst.py`

```python
def test_trend_analysis():
    """Test: Show sales trends over time"""
    agent = DataAnalystAgent(db)
    result = agent.analyze("Show me sales trends for the last 6 months")
    assert result['query_type'] == 'trend'
    assert len(result['charts']) > 0

def test_anomaly_detection():
    """Test: Find late deliveries"""
    agent = DataAnalystAgent(db)
    result = agent.analyze("Detect anomalies in delivery times")
    assert result['query_type'] == 'anomaly'
    assert len(result['anomalies']) > 0

def test_sql_query():
    """Test: SQL-based query"""
    agent = DataAnalystAgent(db)
    result = agent.analyze("What's the average profit by product category?")
    assert result['sql_query'] is not None
    assert result['query_results'] is not None
```

### 6.2 Example Queries
```python
# Example 1: Trend Analysis
query = "Show me monthly sales trends for 2017"
# Expected: Line chart of sales over time

# Example 2: Anomaly Detection
query = "Find orders with unusually high delivery delays"
# Expected: List of late shipments with details

# Example 3: SQL Query
query = "What are the top 5 customers by total sales?"
# Expected: Table with customer names and sales

# Example 4: Multi-dimensional Analysis
query = "Compare profit margins across different shipping modes"
# Expected: Bar chart + statistical summary

# Example 5: Risk Analysis
query = "Which products have the highest late delivery risk?"
# Expected: Risk analysis with recommendations
```

---

## Phase 7: Integration & Deployment

### 7.1 CLI Interface
**File**: `src/cli.py`

```python
import click

@click.command()
@click.option('--query', '-q', help='Analysis query')
def analyze(query: str):
    """Run Data Analyst Agent from CLI"""
    db = SupplyChainDBManager('data')
    agent = DataAnalystAgent(db)
    result = agent.analyze(query)

    print(result['final_response'])
    if result.get('charts'):
        # Save charts to HTML
        pass

if __name__ == '__main__':
    analyze()
```

### 7.2 Opik Integration for Observability

**File**: `src/utils/opik_tracker.py`

**Purpose**: Track agent performance, trace execution, and evaluate responses

```python
from opik import track, opik_context
from opik.integrations.langchain import OpikTracer
import opik

class OpikAgentTracker:
    """Opik integration for Data Analyst Agent"""

    def __init__(self):
        # Initialize Opik client
        self.client = opik.Opik()
        self.tracer = OpikTracer()

    @track(name="data_analyst_query", project_name="omnisupply-data-analyst")
    def track_query(self, query: str, result: dict):
        """Track individual query execution"""
        # Log inputs
        opik_context.update_current_trace(
            input=query,
            output=result.get('final_response'),
            metadata={
                'query_type': result.get('query_type'),
                'sql_query': result.get('sql_query'),
                'num_anomalies': len(result.get('anomalies', [])),
                'num_charts': len(result.get('charts', []))
            }
        )

    def log_node_execution(self, node_name: str, input_data: dict, output_data: dict, duration_ms: float):
        """Log individual node execution for detailed tracing"""
        self.client.log_traces([{
            'name': f'node_{node_name}',
            'input': input_data,
            'output': output_data,
            'metadata': {
                'duration_ms': duration_ms,
                'node_type': node_name
            }
        }])

    def evaluate_response(self, query: str, response: str, ground_truth: str = None):
        """Evaluate response quality using Opik's evaluation framework"""
        from opik.evaluation import evaluate
        from opik.evaluation.metrics import Hallucination, AnswerRelevance

        dataset = [{'input': query, 'output': response}]

        # Evaluate for hallucination and relevance
        evaluate(
            dataset=dataset,
            task=lambda x: {'output': x['output']},
            scoring_metrics=[Hallucination(), AnswerRelevance()],
            experiment_name=f"eval_{query[:30]}"
        )
```

**Integration in Main Agent**:

```python
# In src/agents/data_analyst/agent.py

from src.utils.opik_tracker import OpikAgentTracker
from opik.integrations.langchain import OpikTracer
import time

class DataAnalystAgent:
    def __init__(self, db_manager: SupplyChainDBManager):
        self.db = db_manager
        self.graph = create_data_analyst_graph()
        self.tracker = OpikAgentTracker()  # Add Opik tracker

    def analyze(self, query: str) -> dict:
        """Main entry point with Opik tracing"""
        start_time = time.time()

        initial_state = {
            "user_query": query,
            "messages": [],
            "insights": [],
            "anomalies": [],
            "trends": [],
            "charts": []
        }

        # Execute graph with tracing
        result = self.graph.invoke(
            initial_state,
            config={"callbacks": [OpikTracer()]}  # Enable LangChain callback
        )

        # Track the overall query
        duration = (time.time() - start_time) * 1000
        self.tracker.track_query(query, result)

        return result
```

**Opik Features to Use**:

1. **Automatic Tracing**: Track LLM calls, latency, token usage
2. **Custom Spans**: Log each node execution (parse → SQL → visualize)
3. **Evaluation Metrics**:
   - Hallucination detection (is the SQL query valid?)
   - Answer relevance (does response match query intent?)
   - Custom metrics (e.g., chart quality)
4. **Dataset Management**: Store query/response pairs for regression testing
5. **A/B Testing**: Compare different prompts or models

**Example Usage**:

```python
# Track a query
agent = DataAnalystAgent(db)
result = agent.analyze("Show me sales trends")
# → Automatically logged to Opik with full trace

# Evaluate responses
agent.tracker.evaluate_response(
    query="What's the average profit?",
    response=result['final_response']
)
# → Runs hallucination and relevance checks
```

### 7.3 API Endpoint (Future)
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/analyze")
async def analyze_endpoint(query: str):
    # Return JSON response
    pass
```

---

## Success Metrics

### Phase 1-2 (Setup)
- [ ] All dependencies installed
- [ ] Directory structure created
- [ ] DuckDB database loaded with all 4 datasets
- [ ] Data preprocessing working (encoding issues resolved)

### Phase 3 (Core Agent)
- [ ] LangGraph state machine implemented
- [ ] All 5 nodes functional
- [ ] Graph compiles and runs end-to-end
- [ ] Error handling in place

### Phase 4-5 (Tools & Prompts)
- [ ] SQL tool generates valid queries
- [ ] Anomaly detector finds outliers
- [ ] Charts render correctly
- [ ] Prompts tuned for accuracy

### Phase 6 (Testing)
- [ ] All test cases pass
- [ ] Example queries work as expected
- [ ] Response quality validated

### Phase 7 (Integration & Observability)
- [ ] CLI interface working
- [ ] Opik tracing enabled
- [ ] Evaluation metrics configured
- [ ] Agent traces visible in Comet UI
- [ ] Can be called from other agents (future)

---

## Timeline Estimate

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1 | Setup & Dependencies | 2-3 hours |
| Phase 2 | Data Preparation | 3-4 hours |
| Phase 3 | LangGraph Core | 6-8 hours |
| Phase 4 | Tools Implementation | 3-4 hours |
| Phase 5 | Prompts & Config | 2-3 hours |
| Phase 6 | Testing | 3-4 hours |
| Phase 7 | Integration | 2-3 hours |
| **Total** | | **21-29 hours** |

---

## Key Design Decisions

### Why LangGraph?
- **State Management**: Natural fit for multi-step analysis workflows
- **Routing**: Can intelligently route between SQL, anomaly detection, visualization
- **Observability**: Opik integration for debugging and evaluation
- **Scalability**: Easy to add more nodes later (e.g., ML predictions)

### Why DuckDB?
- **In-memory SQL**: Fast queries on DataFrames
- **No setup**: Embedded database, no separate server
- **Analytics-focused**: Built for OLAP workloads
- **Pandas integration**: Seamless DataFrame ↔ SQL conversion

### Why Plotly?
- **Interactive**: Users can zoom, pan, hover
- **Modern**: Better UX than matplotlib
- **Serializable**: Charts can be saved as JSON
- **Widely supported**: Works in notebooks, web apps, CLI

### Why Opik (Comet)?
- **LangChain Native**: Built-in integration with LangGraph via `OpikTracer`
- **Evaluation Framework**: Pre-built metrics for hallucination, relevance, answer quality
- **Free Tier**: Generous free tier for development and testing
- **Multi-Agent Support**: Track multiple agents in one workspace
- **Dataset Management**: Store and version test datasets for regression testing
- **A/B Testing**: Compare different prompts, models, or configurations
- **Custom Metrics**: Define domain-specific evaluation metrics (e.g., SQL query accuracy)
- **Real-time Monitoring**: Track agent performance in production

**Key Opik Features for This Project**:

1. **Trace Visualization**: See the full execution flow (parse → SQL → visualize → respond)
2. **Token Usage Tracking**: Monitor costs across different query types
3. **Latency Metrics**: Identify slow nodes and optimize
4. **Quality Metrics**:
   - SQL query validity rate
   - Chart generation success rate
   - Anomaly detection precision/recall
5. **Prompt Versioning**: Track prompt changes and their impact on performance
6. **Regression Testing**: Ensure new changes don't break existing queries

---

## Next Steps After Data Analyst Agent

Once this agent is complete:
1. **Supply Chain Risk Agent**: Leverage Data Analyst for trend detection
2. **Finance Insight Agent**: Reuse SQL and visualization tools
3. **Multi-agent orchestration**: Use LangGraph to coordinate agents
4. **Shared knowledge base**: ChromaDB for cross-agent memory

---

## Questions to Resolve

1. **LLM Choice**: OpenAI GPT-4o-mini or GPT-4? (mini for cost, 4 for accuracy)
2. **Caching**: Cache SQL queries for repeated questions?
3. **Streaming**: Stream responses for better UX?
4. **Vector DB**: Should we add semantic search over data insights?
5. **Visualization Output**: Save to files, return JSON, or both?

---

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [DuckDB Python API](https://duckdb.org/docs/api/python/overview)
- [Plotly Python](https://plotly.com/python/)
- [Opik Documentation](https://www.comet.com/docs/opik/)
- [Opik LangChain Integration](https://www.comet.com/docs/opik/tracing/integrations/langchain/)

---

**End of Implementation Plan**
