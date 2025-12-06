"""Finance Insight Agent - P&L reports, expense analysis, and cashflow forecasting"""

from typing import Optional, Dict, Any, List, TypedDict, Literal
from datetime import datetime, timedelta
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
class PLReport(BaseModel):
    """Profit & Loss report"""
    total_revenue: float = Field(description="Total revenue")
    total_cogs: float = Field(description="Total cost of goods sold")
    total_expenses: float = Field(description="Total operating expenses")
    gross_profit: float = Field(description="Revenue - COGS")
    net_profit: float = Field(description="Gross profit - expenses")
    gross_margin_pct: float = Field(description="Gross profit / revenue %")
    net_margin_pct: float = Field(description="Net profit / revenue %")
    period: str = Field(description="Reporting period")


class ExpenseCategory(BaseModel):
    """Expense category breakdown"""
    category: str
    amount: float

class ExpenseAnalysis(BaseModel):
    """Expense analysis with anomalies"""
    total_expenses: float
    expense_by_category: List[ExpenseCategory] = Field(description="List of expense categories with amounts")
    anomalies: List[str] = Field(description="Unusual spending patterns detected")
    top_expense_categories: List[str] = Field(description="Top 3-5 expense categories")
    recommendations: List[str] = Field(description="Cost optimization suggestions")


class CashflowForecast(BaseModel):
    """Cashflow forecast"""
    forecast_period: str = Field(description="Forecast time horizon (e.g., '90 days')")
    projected_revenue: float = Field(description="Projected total revenue")
    projected_expenses: float = Field(description="Projected total expenses")
    projected_cashflow: float = Field(description="Net cashflow projection")
    confidence_level: Literal['LOW', 'MEDIUM', 'HIGH'] = Field(description="Forecast confidence")
    assumptions: List[str] = Field(description="Key forecast assumptions")
    risks: List[str] = Field(description="Risks to forecast")


class KPISummary(BaseModel):
    """Financial KPI summary"""
    revenue_growth_pct: Optional[float] = Field(description="Revenue growth % vs prior period")
    profit_margin_pct: float = Field(description="Overall profit margin %")
    average_order_value: float = Field(description="Average order value")
    customer_ltv: Optional[float] = Field(default=None, description="Customer lifetime value")
    burn_rate: Optional[float] = Field(default=None, description="Monthly cash burn")
    runway_months: Optional[int] = Field(default=None, description="Cash runway in months")


# State for Finance Agent workflow
class FinanceAgentState(TypedDict):
    """State passed between nodes"""
    user_query: str
    pl_report: Optional[PLReport]
    expense_analysis: Optional[ExpenseAnalysis]
    cashflow_forecast: Optional[CashflowForecast]
    kpi_summary: Optional[KPISummary]
    error: Optional[str]


class FinanceAgent(BaseAgent):
    """
    Finance Insight Agent for financial analysis and forecasting.

    Capabilities:
    - P&L report generation
    - Expense analysis and anomaly detection
    - Cashflow forecasting (Prophet-based in future)
    - KPI tracking and trending
    - Financial risk identification
    """

    def __init__(
        self,
        db_client: DatabaseClient,
        vector_store: Optional[OmniSupplyVectorStore] = None,
        llm: Optional[ChatOpenAI] = None
    ):
        """Initialize Finance Agent"""
        # Initialize LLMs for structured outputs
        base_llm = llm or ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            callbacks=[OpikTracer()]
        )

        self.llm_pl = base_llm.with_structured_output(PLReport)
        self.llm_expense = base_llm.with_structured_output(ExpenseAnalysis)
        self.llm_forecast = base_llm.with_structured_output(CashflowForecast)
        self.llm_kpi = base_llm.with_structured_output(KPISummary)

        super().__init__(
            name="finance_agent",
            llm=base_llm,
            db_client=db_client,
            vector_store=vector_store
        )

    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for financial analysis"""
        workflow = StateGraph(FinanceAgentState)

        # Add nodes
        workflow.add_node("generate_pl_report", self.generate_pl_report_node)
        workflow.add_node("analyze_expenses", self.analyze_expenses_node)
        workflow.add_node("forecast_cashflow", self.forecast_cashflow_node)
        workflow.add_node("calculate_kpis", self.calculate_kpis_node)

        # Define edges (linear workflow)
        workflow.set_entry_point("generate_pl_report")
        workflow.add_edge("generate_pl_report", "analyze_expenses")
        workflow.add_edge("analyze_expenses", "forecast_cashflow")
        workflow.add_edge("forecast_cashflow", "calculate_kpis")
        workflow.add_edge("calculate_kpis", END)

        return workflow.compile()

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "P&L report generation",
            "Expense analysis and categorization",
            "Cashflow forecasting",
            "KPI calculation and trending",
            "Financial anomaly detection",
            "Cost optimization recommendations",
            "Revenue analysis"
        ]

    def can_handle(self, query: str) -> float:
        """Determine if this agent can handle the query (0-1 confidence)"""
        query_lower = query.lower()

        # High confidence keywords
        high_confidence = ["finance", "financial", "revenue", "profit", "expense", "cashflow", "forecast"]
        # Medium confidence keywords
        medium_confidence = ["kpi", "margin", "cost", "budget", "p&l", "income", "spending"]

        score = 0.0
        for keyword in high_confidence:
            if keyword in query_lower:
                score += 0.15

        for keyword in medium_confidence:
            if keyword in query_lower:
                score += 0.08

        return min(score, 1.0)

    # ===== Node Functions =====

    def generate_pl_report_node(self, state: FinanceAgentState) -> FinanceAgentState:
        """Generate P&L report from orders and financial data"""
        logger.info("[Finance Agent] Generating P&L report")

        try:
            # Calculate revenue from orders (last 30 days, PostgreSQL syntax)
            revenue_query = f"""
            SELECT
                SUM(sale_price * quantity) as total_revenue,
                SUM((sale_price - profit) * quantity) as total_cogs,
                SUM(profit * quantity) as gross_profit,
                COUNT(*) as total_orders
            FROM orders
            WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
            """

            revenue_results = self.db.execute_query(revenue_query)

            # Calculate expenses from financial transactions
            expense_query = f"""
            SELECT
                SUM(amount) as total_expenses
            FROM financial_transactions
            WHERE transaction_type = 'expense'
            AND transaction_date >= CURRENT_DATE - INTERVAL '30 days'
            """

            expense_results = self.db.execute_query(expense_query)

            # Extract values
            if revenue_results:
                total_revenue = float(revenue_results[0].get('total_revenue', 0) or 0)
                total_cogs = float(revenue_results[0].get('total_cogs', 0) or 0)
                gross_profit = float(revenue_results[0].get('gross_profit', 0) or 0)
            else:
                total_revenue = total_cogs = gross_profit = 0.0

            if expense_results:
                total_expenses = float(expense_results[0].get('total_expenses', 0) or 0)
            else:
                total_expenses = 0.0

            # Calculate derived metrics
            net_profit = gross_profit - total_expenses
            gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0
            net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0.0

            pl_report = PLReport(
                total_revenue=total_revenue,
                total_cogs=total_cogs,
                total_expenses=total_expenses,
                gross_profit=gross_profit,
                net_profit=net_profit,
                gross_margin_pct=gross_margin,
                net_margin_pct=net_margin,
                period="Last 30 days"
            )

            state['pl_report'] = pl_report
            logger.info(f"[Finance Agent] P&L: Revenue ${total_revenue:,.2f}, Net Profit ${net_profit:,.2f}")

        except Exception as e:
            logger.error(f"[Finance Agent] P&L generation error: {e}")
            state['error'] = f"P&L generation failed: {str(e)}"

        return state

    def analyze_expenses_node(self, state: FinanceAgentState) -> FinanceAgentState:
        """Analyze expenses and detect anomalies"""
        logger.info("[Finance Agent] Analyzing expenses")

        try:
            # Get expense breakdown by category (PostgreSQL syntax)
            query = f"""
            SELECT
                category,
                SUM(amount) as total_amount,
                COUNT(*) as transaction_count,
                AVG(amount) as avg_amount,
                MAX(amount) as max_amount
            FROM financial_transactions
            WHERE transaction_type = 'expense'
            AND transaction_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY category
            ORDER BY total_amount DESC
            """

            results = self.db.execute_query(query)

            # Build expense breakdown
            expense_by_category_dict = {r['category']: float(r['total_amount']) for r in results}
            total_expenses = sum(expense_by_category_dict.values())
            top_categories = [r['category'] for r in results[:5]]

            # Convert to list of ExpenseCategory objects
            expense_categories = [
                ExpenseCategory(category=cat, amount=amt)
                for cat, amt in expense_by_category_dict.items()
            ]

            # Prepare data for LLM analysis
            expense_summary = "\n".join([
                f"- {cat}: ${amt:,.2f} ({amt/total_expenses*100:.1f}%)"
                for cat, amt in expense_by_category_dict.items()
            ])

            prompt = f"""Analyze these expense patterns and detect anomalies.

Total Expenses: ${total_expenses:,.2f} (Last 30 days)

Expense Breakdown:
{expense_summary}

Detailed Data:
{results[:10]}

Identify:
1. Any unusual spending patterns or anomalies
2. Top expense categories
3. Cost optimization recommendations
"""

            analysis: ExpenseAnalysis = self.llm_expense.invoke(prompt)

            # Override with calculated values
            analysis.total_expenses = total_expenses
            analysis.expense_by_category = expense_categories
            analysis.top_expense_categories = top_categories

            state['expense_analysis'] = analysis
            logger.info(f"[Finance Agent] Expense analysis: {len(analysis.anomalies)} anomalies detected")

        except Exception as e:
            logger.error(f"[Finance Agent] Expense analysis error: {e}")
            if not state.get('error'):
                state['error'] = f"Expense analysis failed: {str(e)}"

        return state

    def forecast_cashflow_node(self, state: FinanceAgentState) -> FinanceAgentState:
        """Forecast cashflow (simplified version without Prophet)"""
        logger.info("[Finance Agent] Forecasting cashflow")

        try:
            # Get historical revenue and expense trends (PostgreSQL syntax)
            query = f"""
            SELECT
                TO_CHAR(order_date, 'YYYY-MM') as month,
                SUM(sale_price * quantity) as monthly_revenue,
                COUNT(*) as order_count
            FROM orders
            WHERE order_date >= CURRENT_DATE - INTERVAL '180 days'
            GROUP BY TO_CHAR(order_date, 'YYYY-MM')
            ORDER BY TO_CHAR(order_date, 'YYYY-MM') DESC
            """

            revenue_results = self.db.execute_query(query)

            # Simple trend-based forecast (in production, use Prophet)
            if revenue_results and len(revenue_results) >= 2:
                recent_revenue = float(revenue_results[0].get('monthly_revenue', 0) or 0)
                prior_revenue = float(revenue_results[1].get('monthly_revenue', 0) or 0)

                # Calculate growth rate
                growth_rate = ((recent_revenue - prior_revenue) / prior_revenue) if prior_revenue > 0 else 0.0

                # Project 90 days (3 months) forward
                projected_monthly = recent_revenue * (1 + growth_rate)
                projected_revenue = projected_monthly * 3

                # Use expense ratio from P&L
                pl_report = state.get('pl_report')
                if pl_report and pl_report.total_revenue > 0:
                    expense_ratio = (pl_report.total_cogs + pl_report.total_expenses) / pl_report.total_revenue
                    projected_expenses = projected_revenue * expense_ratio
                else:
                    projected_expenses = projected_revenue * 0.7  # Assume 70% expense ratio

                projected_cashflow = projected_revenue - projected_expenses

                # Determine confidence based on data availability
                confidence = 'MEDIUM' if len(revenue_results) >= 3 else 'LOW'

                prompt = f"""Create a cashflow forecast based on these projections.

Historical Data: {len(revenue_results)} months
Recent Monthly Revenue: ${recent_revenue:,.2f}
Growth Rate: {growth_rate:.1%}

90-Day Projections:
- Revenue: ${projected_revenue:,.2f}
- Expenses: ${projected_expenses:,.2f}
- Net Cashflow: ${projected_cashflow:,.2f}

Provide:
1. Key assumptions for this forecast
2. Risks to the forecast
3. Confidence level assessment
"""

                forecast: CashflowForecast = self.llm_forecast.invoke(prompt)

                # Override with calculated values
                forecast.forecast_period = "90 days"
                forecast.projected_revenue = projected_revenue
                forecast.projected_expenses = projected_expenses
                forecast.projected_cashflow = projected_cashflow
                forecast.confidence_level = confidence

                state['cashflow_forecast'] = forecast
                logger.info(f"[Finance Agent] Forecast: ${projected_cashflow:,.2f} ({confidence} confidence)")

            else:
                # Insufficient data
                state['cashflow_forecast'] = CashflowForecast(
                    forecast_period="90 days",
                    projected_revenue=0.0,
                    projected_expenses=0.0,
                    projected_cashflow=0.0,
                    confidence_level='LOW',
                    assumptions=["Insufficient historical data"],
                    risks=["Cannot generate reliable forecast with limited data"]
                )

        except Exception as e:
            logger.error(f"[Finance Agent] Cashflow forecast error: {e}")
            if not state.get('error'):
                state['error'] = f"Cashflow forecast failed: {str(e)}"

        return state

    def calculate_kpis_node(self, state: FinanceAgentState) -> FinanceAgentState:
        """Calculate key financial KPIs"""
        logger.info("[Finance Agent] Calculating KPIs")

        try:
            pl_report = state.get('pl_report')
            cashflow_forecast = state.get('cashflow_forecast')

            # Calculate average order value (PostgreSQL syntax)
            aov_query = f"""
            SELECT
                AVG(sale_price * quantity) as avg_order_value
            FROM orders
            WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
            """

            aov_results = self.db.execute_query(aov_query)
            avg_order_value = float(aov_results[0].get('avg_order_value', 0) or 0) if aov_results else 0.0

            # Calculate revenue growth (compare to prior period)
            growth_query = f"""
            SELECT
                CASE
                    WHEN order_date >= CURRENT_DATE - INTERVAL '30 days' THEN 'current'
                    ELSE 'prior'
                END as period,
                SUM(sale_price * quantity) as revenue
            FROM orders
            WHERE order_date >= CURRENT_DATE - INTERVAL '60 days'
            GROUP BY period
            """

            growth_results = self.db.execute_query(growth_query)
            current_revenue = 0.0
            prior_revenue = 0.0
            for r in growth_results:
                if r['period'] == 'current':
                    current_revenue = float(r['revenue'] or 0)
                else:
                    prior_revenue = float(r['revenue'] or 0)

            revenue_growth = ((current_revenue - prior_revenue) / prior_revenue * 100) if prior_revenue > 0 else 0.0

            # Build KPI summary
            kpi_data = f"""
P&L Report: {pl_report.model_dump_json() if pl_report else 'N/A'}
Average Order Value: ${avg_order_value:,.2f}
Revenue Growth: {revenue_growth:.1f}%
Cashflow Forecast: {cashflow_forecast.model_dump_json() if cashflow_forecast else 'N/A'}
"""

            prompt = f"""Summarize key financial KPIs.

Data:
{kpi_data}

Calculate:
1. Revenue growth % vs prior period
2. Overall profit margin %
3. Average order value
4. Customer LTV (estimate if possible)
5. Burn rate and runway (if applicable)
"""

            kpi_summary: KPISummary = self.llm_kpi.invoke(prompt)

            # Override with calculated values
            kpi_summary.revenue_growth_pct = revenue_growth
            kpi_summary.profit_margin_pct = pl_report.net_margin_pct if pl_report else 0.0
            kpi_summary.average_order_value = avg_order_value

            state['kpi_summary'] = kpi_summary
            logger.info(f"[Finance Agent] KPIs calculated: {kpi_summary.revenue_growth_pct:.1f}% growth")

        except Exception as e:
            logger.error(f"[Finance Agent] KPI calculation error: {e}")
            if not state.get('error'):
                state['error'] = f"KPI calculation failed: {str(e)}"

        return state

    def _format_result(self, state: FinanceAgentState) -> AgentResult:
        """Format workflow state into AgentResult"""
        pl_report = state.get('pl_report')
        expense_analysis = state.get('expense_analysis')
        cashflow_forecast = state.get('cashflow_forecast')
        kpi_summary = state.get('kpi_summary')

        # Build insights
        insights = []

        if pl_report:
            insights.append(f"## P&L Report ({pl_report.period})")
            insights.append(f"- **Revenue**: ${pl_report.total_revenue:,.2f}")
            insights.append(f"- **COGS**: ${pl_report.total_cogs:,.2f}")
            insights.append(f"- **Gross Profit**: ${pl_report.gross_profit:,.2f} ({pl_report.gross_margin_pct:.1f}%)")
            insights.append(f"- **Expenses**: ${pl_report.total_expenses:,.2f}")
            insights.append(f"- **Net Profit**: ${pl_report.net_profit:,.2f} ({pl_report.net_margin_pct:.1f}%)")

        if expense_analysis:
            insights.append(f"\n## Expense Analysis")
            insights.append(f"- **Total Expenses**: ${expense_analysis.total_expenses:,.2f}")
            insights.append(f"- **Top Categories**: {', '.join(expense_analysis.top_expense_categories[:3])}")

            if expense_analysis.anomalies:
                insights.append(f"\n**Anomalies Detected**:")
                insights.extend([f"- {anomaly}" for anomaly in expense_analysis.anomalies])

        if cashflow_forecast:
            insights.append(f"\n## Cashflow Forecast ({cashflow_forecast.forecast_period})")
            insights.append(f"- **Projected Revenue**: ${cashflow_forecast.projected_revenue:,.2f}")
            insights.append(f"- **Projected Expenses**: ${cashflow_forecast.projected_expenses:,.2f}")
            insights.append(f"- **Net Cashflow**: ${cashflow_forecast.projected_cashflow:,.2f}")
            insights.append(f"- **Confidence**: {cashflow_forecast.confidence_level}")

        if kpi_summary:
            insights.append(f"\n## Key KPIs")
            if kpi_summary.revenue_growth_pct is not None:
                insights.append(f"- **Revenue Growth**: {kpi_summary.revenue_growth_pct:.1f}%")
            insights.append(f"- **Profit Margin**: {kpi_summary.profit_margin_pct:.1f}%")
            insights.append(f"- **Avg Order Value**: ${kpi_summary.average_order_value:,.2f}")

        # Build recommendations
        recommendations = []
        if expense_analysis:
            recommendations.extend(expense_analysis.recommendations)

        # Build metrics
        metrics = {
            "net_profit": pl_report.net_profit if pl_report else 0.0,
            "net_margin_pct": pl_report.net_margin_pct if pl_report else 0.0,
            "revenue_growth_pct": kpi_summary.revenue_growth_pct if kpi_summary else 0.0,
            "total_expenses": expense_analysis.total_expenses if expense_analysis else 0.0,
            "projected_cashflow": cashflow_forecast.projected_cashflow if cashflow_forecast else 0.0,
            "forecast_confidence": cashflow_forecast.confidence_level if cashflow_forecast else "N/A"
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
            recommendations=recommendations
        )
