"""Meeting/Report Agent - Executive summaries, weekly reports, and CxO dashboards"""

from typing import Optional, Dict, Any, List, TypedDict, Literal
from datetime import datetime
import logging

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from opik.integrations.langchain import OpikTracer

from .base import BaseAgent, AgentRegistry
from ..data.models import AgentResult
from ..storage.sql.database import DatabaseClient
from ..storage.vector.chromadb_client import OmniSupplyVectorStore

logger = logging.getLogger(__name__)


# Pydantic models for structured outputs
class DataSource(BaseModel):
    """Data aggregated from other agents"""
    source: str = Field(description="Source agent name")
    summary: str = Field(description="Summary of findings")
    key_metrics: Dict[str, Any] = Field(description="Key metrics from source")
    insights: List[str] = Field(default_factory=list, description="Key insights")


class RecommendedAction(BaseModel):
    """Recommended action with priority and owner"""
    action: str = Field(description="The action to take")
    priority: Literal['HIGH', 'MEDIUM', 'LOW']
    owner: str = Field(description="Responsible party (team/role)")
    timeline: str = Field(description="Expected timeline (e.g., 'This week', '2 weeks')")
    rationale: str = Field(description="Why this action is recommended")


class Report(BaseModel):
    """Executive report"""
    report_type: Literal['weekly', 'monthly', 'executive', 'meeting_prep']
    title: str = Field(description="Report title")
    executive_summary: str = Field(description="2-3 paragraph summary for executives")
    key_highlights: List[str] = Field(description="5-7 bullet point highlights")
    recommended_actions: List[RecommendedAction] = Field(description="Top 3-5 recommended actions")
    data_sources: List[str] = Field(description="Which agents/data sources were used")
    report_date: str = Field(description="Report generation date")


# State for Meeting Agent workflow
class MeetingAgentState(TypedDict):
    """State passed between nodes"""
    user_query: str
    report_type: Literal['weekly', 'monthly', 'executive', 'meeting_prep']
    data_sources: Optional[Dict[str, DataSource]]
    report: Optional[Report]
    markdown_output: Optional[str]
    error: Optional[str]


class MeetingAgent(BaseAgent):
    """
    Meeting/Report Agent for executive reporting and CxO summaries.

    Capabilities:
    - Weekly/monthly business reports
    - Executive summaries for CxO
    - Meeting prep documents
    - Cross-functional data aggregation
    - Action item recommendations
    """

    def __init__(
        self,
        db_client: DatabaseClient,
        agent_registry: Optional[AgentRegistry] = None,
        vector_store: Optional[OmniSupplyVectorStore] = None,
        llm: Optional[ChatOpenAI] = None
    ):
        """Initialize Meeting Agent"""
        self.agent_registry = agent_registry

        # Initialize LLMs for structured outputs
        base_llm = llm or ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,  # Slightly higher for more creative summaries
            callbacks=[OpikTracer()]
        )

        self.llm_report = base_llm.with_structured_output(Report)

        super().__init__(
            name="meeting_agent",
            llm=base_llm,
            db_client=db_client,
            vector_store=vector_store
        )

    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for report generation"""
        workflow = StateGraph(MeetingAgentState)

        # Add nodes
        workflow.add_node("determine_report_type", self.determine_report_type_node)
        workflow.add_node("aggregate_data", self.aggregate_data_node)
        workflow.add_node("generate_report", self.generate_report_node)
        workflow.add_node("format_markdown", self.format_markdown_node)

        # Define edges (linear workflow)
        workflow.set_entry_point("determine_report_type")
        workflow.add_edge("determine_report_type", "aggregate_data")
        workflow.add_edge("aggregate_data", "generate_report")
        workflow.add_edge("generate_report", "format_markdown")
        workflow.add_edge("format_markdown", END)

        return workflow.compile()

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "Weekly/monthly business reports",
            "Executive summaries for CxO",
            "Meeting preparation documents",
            "Cross-functional data aggregation",
            "Action item recommendations",
            "KPI dashboard creation"
        ]

    def can_handle(self, query: str) -> float:
        """Determine if this agent can handle the query (0-1 confidence)"""
        query_lower = query.lower()

        # High confidence keywords
        high_confidence = ["report", "summary", "meeting", "executive", "weekly", "monthly", "dashboard"]
        # Medium confidence keywords
        medium_confidence = ["overview", "status", "update", "briefing", "presentation"]

        score = 0.0
        for keyword in high_confidence:
            if keyword in query_lower:
                score += 0.15

        for keyword in medium_confidence:
            if keyword in query_lower:
                score += 0.08

        return min(score, 1.0)

    # ===== Node Functions =====

    def determine_report_type_node(self, state: MeetingAgentState) -> MeetingAgentState:
        """Determine what type of report to generate"""
        logger.info("[Meeting Agent] Determining report type")

        query_lower = state['user_query'].lower()

        # Simple keyword-based classification
        if 'weekly' in query_lower:
            report_type = 'weekly'
        elif 'monthly' in query_lower:
            report_type = 'monthly'
        elif 'executive' in query_lower or 'cxo' in query_lower or 'ceo' in query_lower:
            report_type = 'executive'
        elif 'meeting' in query_lower:
            report_type = 'meeting_prep'
        else:
            # Default to executive
            report_type = 'executive'

        state['report_type'] = report_type
        logger.info(f"[Meeting Agent] Report type: {report_type}")

        return state

    def aggregate_data_node(self, state: MeetingAgentState) -> MeetingAgentState:
        """Aggregate data from other agents"""
        logger.info("[Meeting Agent] Aggregating data from other agents")

        data_sources = {}

        # If agent registry is available, query actual agents
        if self.agent_registry:
            # Query data analyst for metrics
            data_analyst = self.agent_registry.get_agent('data_analyst')
            if data_analyst:
                try:
                    result = data_analyst.execute("Provide key business metrics summary")
                    data_sources['data_analyst'] = DataSource(
                        source='data_analyst',
                        summary=result.insights[0] if result.insights else "No data",
                        key_metrics=result.metrics,
                        insights=result.insights[:3] if result.insights else []
                    )
                except Exception as e:
                    logger.warning(f"[Meeting Agent] Failed to query data_analyst: {e}")

            # Query risk agent for risks
            risk_agent = self.agent_registry.get_agent('risk_agent')
            if risk_agent:
                try:
                    result = risk_agent.execute("What are current supply chain risks?")
                    data_sources['risk_agent'] = DataSource(
                        source='risk_agent',
                        summary=result.insights[0] if result.insights else "No risks",
                        key_metrics=result.metrics,
                        insights=result.insights[:3] if result.insights else []
                    )
                except Exception as e:
                    logger.warning(f"[Meeting Agent] Failed to query risk_agent: {e}")

            # Query finance agent for financial data
            finance_agent = self.agent_registry.get_agent('finance_agent')
            if finance_agent:
                try:
                    result = finance_agent.execute("Provide financial summary")
                    data_sources['finance_agent'] = DataSource(
                        source='finance_agent',
                        summary=result.insights[0] if result.insights else "No data",
                        key_metrics=result.metrics,
                        insights=result.insights[:3] if result.insights else []
                    )
                except Exception as e:
                    logger.warning(f"[Meeting Agent] Failed to query finance_agent: {e}")

        # If no registry or agents available, use mock data from database
        if not data_sources:
            logger.info("[Meeting Agent] Using database queries for data (no agents available)")
            data_sources = self._get_data_from_database()

        state['data_sources'] = data_sources
        logger.info(f"[Meeting Agent] Aggregated {len(data_sources)} data sources")

        return state

    def _get_data_from_database(self) -> Dict[str, DataSource]:
        """Fallback: Get data directly from database"""
        data_sources = {}

        try:
            # Get basic business metrics (PostgreSQL syntax)
            metrics_query = f"""
            SELECT
                COUNT(*) as total_orders,
                SUM(sale_price * quantity) as total_revenue,
                SUM(profit * quantity) as total_profit,
                AVG(sale_price * quantity) as avg_order_value
            FROM orders
            WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
            """
            metrics = self.db.execute_query(metrics_query)

            if metrics:
                m = metrics[0]
                data_sources['business_metrics'] = DataSource(
                    source='database',
                    summary=f"Last 30 days: {m.get('total_orders', 0)} orders, ${m.get('total_revenue', 0):,.2f} revenue",
                    key_metrics={
                        'total_orders': m.get('total_orders', 0),
                        'total_revenue': float(m.get('total_revenue', 0) or 0),
                        'total_profit': float(m.get('total_profit', 0) or 0),
                        'avg_order_value': float(m.get('avg_order_value', 0) or 0)
                    },
                    insights=[
                        f"Total orders: {m.get('total_orders', 0)}",
                        f"Revenue: ${float(m.get('total_revenue', 0) or 0):,.2f}",
                        f"Profit: ${float(m.get('total_profit', 0) or 0):,.2f}"
                    ]
                )

            # Get inventory status
            inventory_query = """
            SELECT
                COUNT(*) as total_items,
                SUM(CASE WHEN stock_quantity <= reorder_level THEN 1 ELSE 0 END) as critical_items
            FROM inventory
            """
            inventory = self.db.execute_query(inventory_query)

            if inventory:
                inv = inventory[0]
                data_sources['inventory_status'] = DataSource(
                    source='database',
                    summary=f"{inv.get('critical_items', 0)} items need reordering",
                    key_metrics={
                        'total_items': inv.get('total_items', 0),
                        'critical_items': inv.get('critical_items', 0)
                    },
                    insights=[f"{inv.get('critical_items', 0)} items below reorder level"]
                )

        except Exception as e:
            logger.error(f"[Meeting Agent] Database query error: {e}")

        return data_sources

    def generate_report_node(self, state: MeetingAgentState) -> MeetingAgentState:
        """Generate structured report using LLM"""
        logger.info("[Meeting Agent] Generating report")

        report_type = state['report_type']
        data_sources = state.get('data_sources', {})

        # Format data sources for prompt
        data_summary = "\n\n".join([
            f"**{source.source}**:\n{source.summary}\nKey Metrics: {source.key_metrics}\nInsights: {', '.join(source.insights)}"
            for source in data_sources.values()
        ])

        prompt = f"""Generate a {report_type} business report based on this data.

User Request: {state['user_query']}

Data Sources:
{data_summary}

Create a comprehensive report with:
1. Executive summary (2-3 paragraphs for CxO level)
2. 5-7 key highlights (bullet points)
3. Top 3-5 recommended actions with:
   - Priority (HIGH/MEDIUM/LOW)
   - Owner (which team/role)
   - Timeline
   - Rationale

Make it actionable and focused on business outcomes.
"""

        try:
            report: Report = self.llm_report.invoke(prompt)

            # Override report metadata
            report.report_type = report_type
            report.data_sources = list(data_sources.keys())
            report.report_date = datetime.utcnow().strftime("%Y-%m-%d")

            state['report'] = report
            logger.info(f"[Meeting Agent] Report generated: {report.title}")

        except Exception as e:
            logger.error(f"[Meeting Agent] Report generation error: {e}")
            state['error'] = f"Report generation failed: {str(e)}"

        return state

    def format_markdown_node(self, state: MeetingAgentState) -> MeetingAgentState:
        """Format report as markdown"""
        logger.info("[Meeting Agent] Formatting report as markdown")

        report = state.get('report')
        if not report:
            state['markdown_output'] = "# Error\n\nNo report generated."
            return state

        # Build markdown document
        markdown = f"""# {report.title}

**Report Type**: {report.report_type.title()}
**Date**: {report.report_date}
**Data Sources**: {', '.join(report.data_sources)}

---

## Executive Summary

{report.executive_summary}

---

## Key Highlights

"""

        for highlight in report.key_highlights:
            markdown += f"- {highlight}\n"

        markdown += "\n---\n\n## Recommended Actions\n\n"

        for i, action in enumerate(report.recommended_actions, 1):
            markdown += f"""### {i}. {action.action}

- **Priority**: {action.priority}
- **Owner**: {action.owner}
- **Timeline**: {action.timeline}
- **Rationale**: {action.rationale}

"""

        markdown += "\n---\n\n*Report generated by OmniSupply Meeting Agent*\n"

        state['markdown_output'] = markdown
        logger.info("[Meeting Agent] Markdown formatting complete")

        return state

    def _format_result(self, state: MeetingAgentState) -> AgentResult:
        """Format workflow state into AgentResult"""
        report = state.get('report')
        markdown = state.get('markdown_output')

        # Build insights
        insights = []
        if report:
            insights.append(f"## {report.title}")
            insights.append(f"\n**Executive Summary**:\n{report.executive_summary}")
            insights.append(f"\n**Key Highlights**:")
            insights.extend([f"- {h}" for h in report.key_highlights])

        # Build recommendations
        recommendations = []
        if report:
            for action in report.recommended_actions:
                recommendations.append(
                    f"[{action.priority}] {action.action} (Owner: {action.owner}, Timeline: {action.timeline})"
                )

        # Build metrics
        metrics = {
            "report_type": report.report_type if report else "unknown",
            "data_sources_count": len(report.data_sources) if report else 0,
            "actions_count": len(report.recommended_actions) if report else 0,
            "report_date": report.report_date if report else None
        }

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
            raw_data={'markdown_report': markdown} if markdown else None
        )
