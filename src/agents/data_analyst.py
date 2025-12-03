"""Data Analyst Agent - SQL query generation, visualization, and anomaly detection"""

from typing import Optional, Dict, Any, List, TypedDict
from datetime import datetime
from decimal import Decimal
import logging

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from opik.integrations.langchain import OpikTracer

from .base import BaseAgent
from ..data.models import AgentResult
from ..storage.sql.database import DatabaseClient
from ..storage.vector.chromadb_client import OmniSupplyVectorStore

logger = logging.getLogger(__name__)


# Pydantic models for structured outputs
class QueryEntities(BaseModel):
    """Entities extracted from query"""
    metrics: List[str] = Field(default_factory=list, description="Metrics to calculate (e.g., revenue, profit)")
    dimensions: List[str] = Field(default_factory=list, description="Dimensions to group by (e.g., category, region)")
    filters: List[str] = Field(default_factory=list, description="Filter conditions")
    time_period: Optional[str] = Field(default=None, description="Time period mentioned")


class QueryClassification(BaseModel):
    """Classification of user query intent"""
    query_type: str = Field(description="Type: 'aggregation', 'trend', 'comparison', 'anomaly', 'detail'")
    entities: QueryEntities = Field(default_factory=QueryEntities)
    confidence: float = Field(description="Confidence score 0-1")
    reasoning: str = Field(description="Why this classification")


class SQLQuery(BaseModel):
    """Generated SQL query with metadata"""
    sql: str = Field(description="The SQL query to execute")
    explanation: str = Field(description="What this query does")
    expected_columns: List[str] = Field(description="Expected result columns")


class AnalysisResult(BaseModel):
    """Analysis findings from query results"""
    summary: str = Field(description="Summary of findings")
    key_insights: List[str] = Field(description="3-5 key insights")
    anomalies: List[str] = Field(default_factory=list, description="Any anomalies detected")
    recommendations: List[str] = Field(default_factory=list, description="Recommended actions")


# State for Data Analyst workflow
class DataAnalystState(TypedDict):
    """State passed between nodes"""
    user_query: str
    classification: Optional[QueryClassification]
    sql_query: Optional[SQLQuery]
    query_results: Optional[List[Dict]]
    analysis: Optional[AnalysisResult]
    visualizations: Optional[List[Dict]]
    error: Optional[str]
    retry_count: int


class DataAnalystAgent(BaseAgent):
    """
    Data Analyst Agent for SQL query generation, data analysis, and visualization.

    Capabilities:
    - Natural language to SQL conversion
    - Query execution and result analysis
    - Anomaly detection
    - Data visualization recommendations
    - Trend analysis
    """

    def __init__(
        self,
        db_client: DatabaseClient,
        vector_store: Optional[OmniSupplyVectorStore] = None,
        llm: Optional[ChatOpenAI] = None
    ):
        """Initialize Data Analyst Agent"""
        self.max_retries = 2

        # Initialize LLMs for structured outputs
        base_llm = llm or ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            callbacks=[OpikTracer()]
        )

        self.llm_classifier = base_llm.with_structured_output(QueryClassification)
        self.llm_sql = base_llm.with_structured_output(SQLQuery)
        self.llm_analyzer = base_llm.with_structured_output(AnalysisResult)

        super().__init__(
            name="data_analyst",
            llm=base_llm,
            db_client=db_client,
            vector_store=vector_store
        )

    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for data analysis"""
        workflow = StateGraph(DataAnalystState)

        # Add nodes
        workflow.add_node("parse_query", self.parse_query_node)
        workflow.add_node("generate_sql", self.generate_sql_node)
        workflow.add_node("execute_query", self.execute_query_node)
        workflow.add_node("analyze_results", self.analyze_results_node)
        workflow.add_node("create_visualizations", self.create_visualizations_node)
        workflow.add_node("generate_response", self.generate_response_node)

        # Define edges
        workflow.set_entry_point("parse_query")
        workflow.add_edge("parse_query", "generate_sql")
        workflow.add_edge("generate_sql", "execute_query")

        # Conditional edge: if error and retries left, go back to generate_sql
        workflow.add_conditional_edges(
            "execute_query",
            self._route_after_execution,
            {
                "analyze": "analyze_results",
                "retry": "generate_sql",
                "end": END
            }
        )

        workflow.add_edge("analyze_results", "create_visualizations")
        workflow.add_edge("create_visualizations", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "SQL query generation from natural language",
            "Data aggregation and analysis",
            "Trend identification",
            "Anomaly detection",
            "Data visualization recommendations",
            "KPI calculation",
            "Comparative analysis"
        ]

    def can_handle(self, query: str) -> float:
        """Determine if this agent can handle the query (0-1 confidence)"""
        query_lower = query.lower()

        # High confidence keywords
        high_confidence = ["data", "query", "sql", "show", "analyze", "calculate", "trend", "compare"]
        # Medium confidence keywords
        medium_confidence = ["revenue", "sales", "orders", "products", "kpi", "metrics"]

        score = 0.0
        for keyword in high_confidence:
            if keyword in query_lower:
                score += 0.15

        for keyword in medium_confidence:
            if keyword in query_lower:
                score += 0.08

        return min(score, 1.0)

    # ===== Node Functions =====

    def parse_query_node(self, state: DataAnalystState) -> DataAnalystState:
        """Parse and classify the user query"""
        logger.info(f"[Data Analyst] Parsing query: {state['user_query']}")

        prompt = f"""Classify this data analysis query and extract entities.

User Query: {state['user_query']}

Available tables and columns:
- orders: order_id, order_date, category, product_id, sale_price, profit, quantity, discount_percent, is_returned, segment, region, state
- shipments: shipment_id, carrier, shipment_date, expected_delivery, actual_delivery, status, origin_location, destination_location
- inventory: sku, product_id, product_name, stock_quantity, reorder_level, warehouse_location
- financial_transactions: transaction_id, transaction_date, transaction_type, category, amount, payment_status

Determine:
1. Query type (aggregation, trend, comparison, anomaly, detail)
2. Metrics to calculate
3. Dimensions to group by
4. Any filters mentioned
5. Time period if mentioned
"""

        try:
            classification: QueryClassification = self.llm_classifier.invoke(prompt)
            state['classification'] = classification
            logger.info(f"[Data Analyst] Classification: {classification.query_type} (confidence: {classification.confidence})")
        except Exception as e:
            logger.error(f"[Data Analyst] Classification error: {e}")
            state['error'] = f"Query classification failed: {str(e)}"

        return state

    def generate_sql_node(self, state: DataAnalystState) -> DataAnalystState:
        """Generate SQL query based on classification"""
        logger.info("[Data Analyst] Generating SQL query")

        if state.get('error') and state.get('retry_count', 0) >= self.max_retries:
            return state

        classification = state.get('classification')
        if not classification:
            state['error'] = "No classification available"
            return state

        # Include previous error for retry context
        error_context = ""
        if state.get('error') and state.get('retry_count', 0) > 0:
            error_context = f"\n\nPrevious attempt failed with error: {state['error']}\nPlease fix the SQL query."

        prompt = f"""Generate a SQL query for this analysis request.

User Query: {state['user_query']}

Classification:
- Type: {classification.query_type}
- Metrics: {', '.join(classification.entities.metrics) if classification.entities.metrics else 'None'}
- Dimensions: {', '.join(classification.entities.dimensions) if classification.entities.dimensions else 'None'}
- Filters: {', '.join(classification.entities.filters) if classification.entities.filters else 'None'}
- Time Period: {classification.entities.time_period or 'Not specified'}

Available tables:
- orders (order_id, order_date, category, product_id, sale_price, profit, quantity, discount_percent, is_returned, segment, region, state)
- shipments (shipment_id, carrier, shipment_date, expected_delivery, actual_delivery, status)
- inventory (sku, product_id, product_name, stock_quantity, reorder_level, warehouse_location)
- financial_transactions (transaction_id, transaction_date, transaction_type, category, amount, payment_status)

Generate valid DuckDB/PostgreSQL SQL. Use proper date functions. Limit results to 100 rows.{error_context}
"""

        try:
            sql_query: SQLQuery = self.llm_sql.invoke(prompt)
            state['sql_query'] = sql_query
            logger.info(f"[Data Analyst] Generated SQL: {sql_query.sql[:100]}...")

            # Clear previous error on retry
            if 'error' in state:
                del state['error']
        except Exception as e:
            logger.error(f"[Data Analyst] SQL generation error: {e}")
            state['error'] = f"SQL generation failed: {str(e)}"

        return state

    def execute_query_node(self, state: DataAnalystState) -> DataAnalystState:
        """Execute the generated SQL query"""
        logger.info("[Data Analyst] Executing SQL query")

        sql_query = state.get('sql_query')
        if not sql_query:
            state['error'] = "No SQL query to execute"
            return state

        try:
            results = self.db.execute_query(sql_query.sql)
            state['query_results'] = results
            logger.info(f"[Data Analyst] Query returned {len(results)} rows")

            # Clear error on success
            if 'error' in state:
                del state['error']
        except Exception as e:
            logger.error(f"[Data Analyst] Query execution error: {e}")
            state['error'] = f"Query execution failed: {str(e)}"
            state['retry_count'] = state.get('retry_count', 0) + 1

        return state

    def _route_after_execution(self, state: DataAnalystState) -> str:
        """Route based on execution success/failure"""
        if state.get('error'):
            if state.get('retry_count', 0) < self.max_retries:
                logger.info(f"[Data Analyst] Retrying (attempt {state.get('retry_count', 0) + 1})")
                return "retry"
            else:
                logger.error("[Data Analyst] Max retries reached")
                return "end"
        return "analyze"

    def analyze_results_node(self, state: DataAnalystState) -> DataAnalystState:
        """Analyze query results and extract insights"""
        logger.info("[Data Analyst] Analyzing results")

        results = state.get('query_results', [])
        if not results:
            state['analysis'] = AnalysisResult(
                summary="No data returned from query.",
                key_insights=["Query returned no results"],
                anomalies=[],
                recommendations=["Verify data availability and query filters"]
            )
            return state

        # Format results for LLM analysis
        results_sample = results[:10]  # First 10 rows
        results_str = "\n".join([str(row) for row in results_sample])

        prompt = f"""Analyze these query results and provide insights.

User Query: {state['user_query']}

Query Results ({len(results)} total rows, showing first 10):
{results_str}

Provide:
1. Summary of findings (2-3 sentences)
2. 3-5 key insights
3. Any anomalies detected (outliers, unusual patterns)
4. Recommended actions based on findings
"""

        try:
            analysis: AnalysisResult = self.llm_analyzer.invoke(prompt)
            state['analysis'] = analysis
            logger.info(f"[Data Analyst] Analysis complete: {len(analysis.key_insights)} insights")
        except Exception as e:
            logger.error(f"[Data Analyst] Analysis error: {e}")
            state['analysis'] = AnalysisResult(
                summary="Analysis failed due to processing error.",
                key_insights=["Unable to complete analysis"],
                anomalies=[],
                recommendations=[]
            )

        return state

    def create_visualizations_node(self, state: DataAnalystState) -> DataAnalystState:
        """Recommend visualizations for the data"""
        logger.info("[Data Analyst] Creating visualization recommendations")

        classification = state.get('classification')
        results = state.get('query_results', [])

        if not results:
            state['visualizations'] = []
            return state

        # Simple rule-based visualization recommendations
        viz_recommendations = []

        if classification:
            query_type = classification.query_type

            if query_type == "aggregation":
                viz_recommendations.append({
                    "type": "bar_chart",
                    "description": "Bar chart showing aggregated metrics by dimension",
                    "suitable_for": "Comparing values across categories"
                })

            elif query_type == "trend":
                viz_recommendations.append({
                    "type": "line_chart",
                    "description": "Line chart showing metric trends over time",
                    "suitable_for": "Tracking changes over time periods"
                })

            elif query_type == "comparison":
                viz_recommendations.append({
                    "type": "grouped_bar_chart",
                    "description": "Grouped bar chart for multi-dimensional comparison",
                    "suitable_for": "Comparing multiple metrics across categories"
                })

            elif query_type == "anomaly":
                viz_recommendations.append({
                    "type": "scatter_plot",
                    "description": "Scatter plot to visualize outliers and distributions",
                    "suitable_for": "Identifying anomalies and patterns"
                })

            else:
                viz_recommendations.append({
                    "type": "table",
                    "description": "Detailed table view of results",
                    "suitable_for": "Examining detailed records"
                })

        state['visualizations'] = viz_recommendations
        logger.info(f"[Data Analyst] Recommended {len(viz_recommendations)} visualizations")

        return state

    def generate_response_node(self, state: DataAnalystState) -> DataAnalystState:
        """Generate final response (handled by _format_result)"""
        logger.info("[Data Analyst] Generating response")
        return state

    def _format_result(self, state: DataAnalystState) -> AgentResult:
        """Format workflow state into AgentResult"""
        analysis = state.get('analysis')
        results = state.get('query_results', [])
        viz = state.get('visualizations', [])
        sql_query = state.get('sql_query')

        # Build insights
        insights = []
        if analysis:
            insights.append(f"**Summary**: {analysis.summary}")
            insights.extend([f"- {insight}" for insight in analysis.key_insights])

            if analysis.anomalies:
                insights.append(f"\n**Anomalies Detected**:")
                insights.extend([f"- {anomaly}" for anomaly in analysis.anomalies])

        # Build recommendations
        recommendations = analysis.recommendations if analysis else []

        # Build metrics
        metrics = {
            "rows_returned": len(results),
            "sql_query": sql_query.sql if sql_query else None,
            "query_type": state.get('classification').query_type if state.get('classification') else None,
            "visualizations_recommended": len(viz)
        }

        # Add error info if present
        if state.get('error'):
            insights.append(f"\n**Error**: {state['error']}")
            metrics['error'] = state['error']

        return AgentResult(
            agent_name=self.name,
            query=state['user_query'],
            timestamp=datetime.utcnow(),
            success=not bool(state.get('error')),
            insights=insights,
            metrics=metrics,
            recommendations=recommendations,
            raw_data=results[:20] if results else None  # Include sample of results
        )
