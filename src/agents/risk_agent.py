"""Supply Chain Risk Agent - Multi-dimensional risk assessment and alerting"""

from typing import Optional, Dict, Any, List, TypedDict, Literal
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from opik.integrations.langchain import OpikTracer

from .base import BaseAgent
from ..data.models import AgentResult, RiskAssessment
from ..storage.sql.database import DatabaseClient
from ..storage.vector.chromadb_client import OmniSupplyVectorStore

logger = logging.getLogger(__name__)


# Pydantic models for structured outputs
class RiskScore(BaseModel):
    """Individual risk score"""
    category: str = Field(description="Risk category (delivery, inventory, quality, financial)")
    score: float = Field(description="Risk score 0-1 (0=low, 1=critical)")
    severity: Literal['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    contributing_factors: List[str] = Field(description="What's causing this risk")
    affected_entities: List[str] = Field(description="What's affected (products, regions, etc.)")


class OverallRiskAssessment(BaseModel):
    """Complete risk assessment"""
    overall_score: float = Field(description="Weighted overall risk 0-1")
    overall_severity: Literal['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    risk_scores: List[RiskScore] = Field(description="Individual risk category scores")
    top_risks: List[str] = Field(description="Top 3-5 risks to address")
    recommended_actions: List[str] = Field(description="Immediate actions needed")
    monitoring_items: List[str] = Field(description="Items to monitor closely")


class AlertRecommendation(BaseModel):
    """Alert recommendation"""
    should_alert: bool = Field(description="Whether to send alert")
    severity: Literal['INFO', 'WARNING', 'CRITICAL']
    recipients: List[str] = Field(description="Who should receive alert")
    message: str = Field(description="Alert message")


# State for Risk Agent workflow
class RiskAgentState(TypedDict):
    """State passed between nodes"""
    user_query: str
    delivery_data: Optional[Dict[str, Any]]
    inventory_data: Optional[Dict[str, Any]]
    quality_data: Optional[Dict[str, Any]]
    financial_data: Optional[Dict[str, Any]]
    risk_assessment: Optional[OverallRiskAssessment]
    alert_recommendation: Optional[AlertRecommendation]
    error: Optional[str]


class RiskAgent(BaseAgent):
    """
    Supply Chain Risk Agent for multi-dimensional risk assessment.

    Capabilities:
    - Delivery risk analysis (late shipments, carrier performance)
    - Inventory risk analysis (stockouts, overstock, reorder levels)
    - Quality risk analysis (returns, defects)
    - Financial risk analysis (margins, discounts, payment issues)
    - Weighted aggregate risk scoring
    - Alert generation
    """

    def __init__(
        self,
        db_client: DatabaseClient,
        vector_store: Optional[OmniSupplyVectorStore] = None,
        llm: Optional[ChatOpenAI] = None
    ):
        """Initialize Risk Agent"""
        # Risk weights for aggregate scoring
        self.risk_weights = {
            'delivery': 0.4,
            'inventory': 0.3,
            'quality': 0.2,
            'financial': 0.1
        }

        # Severity thresholds
        self.severity_thresholds = {
            'CRITICAL': 0.7,
            'HIGH': 0.5,
            'MEDIUM': 0.3,
            'LOW': 0.0
        }

        # Initialize LLMs for structured outputs
        base_llm = llm or ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            callbacks=[OpikTracer()]
        )

        self.llm_risk_assessor = base_llm.with_structured_output(OverallRiskAssessment)
        self.llm_alerter = base_llm.with_structured_output(AlertRecommendation)

        super().__init__(
            name="risk_agent",
            llm=base_llm,
            db_client=db_client,
            vector_store=vector_store
        )

    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for risk assessment"""
        workflow = StateGraph(RiskAgentState)

        # Add nodes
        workflow.add_node("gather_delivery_data", self.gather_delivery_data_node)
        workflow.add_node("gather_inventory_data", self.gather_inventory_data_node)
        workflow.add_node("gather_quality_data", self.gather_quality_data_node)
        workflow.add_node("gather_financial_data", self.gather_financial_data_node)
        workflow.add_node("assess_risks", self.assess_risks_node)
        workflow.add_node("generate_alerts", self.generate_alerts_node)

        # Define edges (linear workflow - all data gathering in parallel conceptually)
        workflow.set_entry_point("gather_delivery_data")
        workflow.add_edge("gather_delivery_data", "gather_inventory_data")
        workflow.add_edge("gather_inventory_data", "gather_quality_data")
        workflow.add_edge("gather_quality_data", "gather_financial_data")
        workflow.add_edge("gather_financial_data", "assess_risks")
        workflow.add_edge("assess_risks", "generate_alerts")
        workflow.add_edge("generate_alerts", END)

        return workflow.compile()

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "Delivery risk assessment (late shipments, carrier issues)",
            "Inventory risk assessment (stockouts, overstock)",
            "Quality risk assessment (returns, defects)",
            "Financial risk assessment (margins, discounts)",
            "Multi-dimensional risk scoring",
            "Alert generation and prioritization",
            "Risk trend analysis"
        ]

    def can_handle(self, query: str) -> float:
        """Determine if this agent can handle the query (0-1 confidence)"""
        query_lower = query.lower()

        # High confidence keywords
        high_confidence = ["risk", "alert", "critical", "issue", "problem", "delay", "late"]
        # Medium confidence keywords
        medium_confidence = ["delivery", "inventory", "stockout", "shortage", "quality", "defect", "margin"]

        score = 0.0
        for keyword in high_confidence:
            if keyword in query_lower:
                score += 0.15

        for keyword in medium_confidence:
            if keyword in query_lower:
                score += 0.08

        return min(score, 1.0)

    # ===== Node Functions =====

    def gather_delivery_data_node(self, state: RiskAgentState) -> RiskAgentState:
        """Gather delivery risk data"""
        logger.info("[Risk Agent] Gathering delivery data")

        try:
            # Calculate late shipment rate (PostgreSQL syntax)
            query = f"""
            SELECT
                COUNT(*) as total_shipments,
                SUM(CASE WHEN actual_delivery > expected_delivery THEN 1 ELSE 0 END) as late_shipments,
                AVG(EXTRACT(EPOCH FROM (actual_delivery - expected_delivery))/86400) as avg_delay_days,
                carrier,
                COUNT(DISTINCT CASE WHEN actual_delivery > expected_delivery THEN carrier END) as carriers_with_issues
            FROM shipments
            WHERE shipment_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY carrier
            ORDER BY late_shipments DESC
            LIMIT 10
            """

            results = self.db.execute_query(query)

            # Calculate overall metrics
            total = sum(r.get('total_shipments', 0) for r in results)
            late = sum(r.get('late_shipments', 0) for r in results)
            late_rate = (late / total) if total > 0 else 0.0

            state['delivery_data'] = {
                'late_rate': late_rate,
                'total_shipments': total,
                'late_shipments': late,
                'carrier_performance': results[:5],
                'risk_score': late_rate  # 0-1 score
            }

            logger.info(f"[Risk Agent] Delivery risk score: {late_rate:.2f}")
        except Exception as e:
            logger.error(f"[Risk Agent] Delivery data error: {e}")
            state['delivery_data'] = {'risk_score': 0.0, 'error': str(e)}

        return state

    def gather_inventory_data_node(self, state: RiskAgentState) -> RiskAgentState:
        """Gather inventory risk data"""
        logger.info("[Risk Agent] Gathering inventory data")

        try:
            # Find critical inventory items
            query = """
            SELECT
                COUNT(*) as total_items,
                SUM(CASE WHEN stock_quantity <= reorder_level THEN 1 ELSE 0 END) as critical_items,
                SUM(CASE WHEN stock_quantity = 0 THEN 1 ELSE 0 END) as stockout_items,
                SUM(CASE WHEN stock_quantity > reorder_level * 3 THEN 1 ELSE 0 END) as overstock_items,
                product_name,
                stock_quantity,
                reorder_level
            FROM inventory
            GROUP BY product_name, stock_quantity, reorder_level
            ORDER BY
                CASE
                    WHEN stock_quantity = 0 THEN 1
                    WHEN stock_quantity <= reorder_level THEN 2
                    ELSE 3
                END
            LIMIT 10
            """

            results = self.db.execute_query(query)

            # Calculate overall metrics
            total_items = results[0].get('total_items', 0) if results else 0
            critical_items = sum(r.get('critical_items', 0) for r in results)
            stockout_items = sum(r.get('stockout_items', 0) for r in results)

            critical_pct = (critical_items / total_items) if total_items > 0 else 0.0

            state['inventory_data'] = {
                'critical_pct': critical_pct,
                'total_items': total_items,
                'critical_items': critical_items,
                'stockout_items': stockout_items,
                'critical_products': results[:5],
                'risk_score': critical_pct  # 0-1 score
            }

            logger.info(f"[Risk Agent] Inventory risk score: {critical_pct:.2f}")
        except Exception as e:
            logger.error(f"[Risk Agent] Inventory data error: {e}")
            state['inventory_data'] = {'risk_score': 0.0, 'error': str(e)}

        return state

    def gather_quality_data_node(self, state: RiskAgentState) -> RiskAgentState:
        """Gather quality risk data"""
        logger.info("[Risk Agent] Gathering quality data")

        try:
            # Calculate return and defect rates (PostgreSQL syntax with boolean support)
            query = f"""
            SELECT
                COUNT(*) as total_orders,
                SUM(CASE WHEN is_returned THEN 1 ELSE 0 END) as returned_orders,
                CAST(SUM(CASE WHEN is_returned THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as return_rate,
                category,
                product_id
            FROM orders
            WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY category, product_id
            HAVING CAST(SUM(CASE WHEN is_returned THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) > 0
            ORDER BY return_rate DESC
            LIMIT 10
            """

            results = self.db.execute_query(query)

            # Calculate overall metrics
            if results:
                total_orders = sum(r.get('total_orders', 0) for r in results)
                returned_orders = sum(r.get('returned_orders', 0) for r in results)
                return_rate = (returned_orders / total_orders) if total_orders > 0 else 0.0
            else:
                return_rate = 0.0
                total_orders = 0
                returned_orders = 0

            state['quality_data'] = {
                'return_rate': return_rate,
                'total_orders': total_orders,
                'returned_orders': returned_orders,
                'high_return_products': results[:5],
                'risk_score': return_rate  # 0-1 score
            }

            logger.info(f"[Risk Agent] Quality risk score: {return_rate:.2f}")
        except Exception as e:
            logger.error(f"[Risk Agent] Quality data error: {e}")
            state['quality_data'] = {'risk_score': 0.0, 'error': str(e)}

        return state

    def gather_financial_data_node(self, state: RiskAgentState) -> RiskAgentState:
        """Gather financial risk data"""
        logger.info("[Risk Agent] Gathering financial data")

        try:
            # Calculate margin and discount risks (PostgreSQL syntax)
            query = f"""
            SELECT
                COUNT(*) as total_orders,
                AVG(profit / NULLIF(sale_price, 0)) as avg_margin,
                AVG(discount_percent) as avg_discount,
                SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) as negative_profit_orders,
                SUM(CASE WHEN discount_percent > 30 THEN 1 ELSE 0 END) as high_discount_orders,
                category
            FROM orders
            WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY category
            ORDER BY avg_margin ASC
            LIMIT 10
            """

            results = self.db.execute_query(query)

            # Calculate overall metrics
            if results:
                total_orders = sum(r.get('total_orders', 0) for r in results)
                negative_orders = sum(r.get('negative_profit_orders', 0) for r in results)
                high_discount = sum(r.get('high_discount_orders', 0) for r in results)

                risk_rate = ((negative_orders + high_discount) / total_orders) if total_orders > 0 else 0.0
            else:
                risk_rate = 0.0
                total_orders = 0

            state['financial_data'] = {
                'risk_rate': risk_rate,
                'total_orders': total_orders,
                'negative_profit_orders': negative_orders if results else 0,
                'high_discount_orders': high_discount if results else 0,
                'at_risk_categories': results[:5],
                'risk_score': risk_rate  # 0-1 score
            }

            logger.info(f"[Risk Agent] Financial risk score: {risk_rate:.2f}")
        except Exception as e:
            logger.error(f"[Risk Agent] Financial data error: {e}")
            state['financial_data'] = {'risk_score': 0.0, 'error': str(e)}

        return state

    def assess_risks_node(self, state: RiskAgentState) -> RiskAgentState:
        """Assess overall risks using LLM"""
        logger.info("[Risk Agent] Assessing overall risks")

        # Extract risk scores
        delivery_score = state.get('delivery_data', {}).get('risk_score', 0.0)
        inventory_score = state.get('inventory_data', {}).get('risk_score', 0.0)
        quality_score = state.get('quality_data', {}).get('risk_score', 0.0)
        financial_score = state.get('financial_data', {}).get('risk_score', 0.0)

        # Calculate weighted overall score
        overall_score = (
            delivery_score * self.risk_weights['delivery'] +
            inventory_score * self.risk_weights['inventory'] +
            quality_score * self.risk_weights['quality'] +
            financial_score * self.risk_weights['financial']
        )

        # Determine overall severity
        overall_severity = self._classify_severity(overall_score)

        prompt = f"""Assess supply chain risks based on these metrics.

**Delivery Risk** (weight 40%):
- Late shipment rate: {delivery_score:.1%}
- Risk score: {delivery_score:.2f}
- Data: {state.get('delivery_data')}

**Inventory Risk** (weight 30%):
- Critical inventory percentage: {inventory_score:.1%}
- Risk score: {inventory_score:.2f}
- Data: {state.get('inventory_data')}

**Quality Risk** (weight 20%):
- Return rate: {quality_score:.1%}
- Risk score: {quality_score:.2f}
- Data: {state.get('quality_data')}

**Financial Risk** (weight 10%):
- At-risk order rate: {financial_score:.1%}
- Risk score: {financial_score:.2f}
- Data: {state.get('financial_data')}

**Overall Risk Score**: {overall_score:.2f} ({overall_severity})

Provide:
1. Individual risk scores with severity for each category
2. Contributing factors for each risk
3. Affected entities (products, carriers, regions)
4. Top 3-5 risks to address immediately
5. Recommended actions
6. Items to monitor closely
"""

        try:
            assessment: OverallRiskAssessment = self.llm_risk_assessor.invoke(prompt)

            # Override with calculated values
            assessment.overall_score = overall_score
            assessment.overall_severity = overall_severity

            state['risk_assessment'] = assessment
            logger.info(f"[Risk Agent] Assessment complete: {overall_severity} ({overall_score:.2f})")
        except Exception as e:
            logger.error(f"[Risk Agent] Assessment error: {e}")
            state['error'] = f"Risk assessment failed: {str(e)}"

        return state

    def generate_alerts_node(self, state: RiskAgentState) -> RiskAgentState:
        """Generate alert recommendations"""
        logger.info("[Risk Agent] Generating alerts")

        assessment = state.get('risk_assessment')
        if not assessment:
            state['alert_recommendation'] = AlertRecommendation(
                should_alert=False,
                severity='INFO',
                recipients=[],
                message="No risk assessment available"
            )
            return state

        prompt = f"""Determine if alerts should be sent based on this risk assessment.

Overall Risk: {assessment.overall_severity} (score: {assessment.overall_score:.2f})

Top Risks:
{chr(10).join([f"- {risk}" for risk in assessment.top_risks])}

Recommended Actions:
{chr(10).join([f"- {action}" for action in assessment.recommended_actions])}

Determine:
1. Should we send an alert? (Yes if CRITICAL or HIGH)
2. Alert severity (INFO, WARNING, CRITICAL)
3. Who should receive it (operations, finance, executives)
4. Alert message (concise, actionable)
"""

        try:
            alert: AlertRecommendation = self.llm_alerter.invoke(prompt)
            state['alert_recommendation'] = alert
            logger.info(f"[Risk Agent] Alert: {alert.should_alert} ({alert.severity})")
        except Exception as e:
            logger.error(f"[Risk Agent] Alert generation error: {e}")
            state['alert_recommendation'] = AlertRecommendation(
                should_alert=False,
                severity='INFO',
                recipients=[],
                message="Alert generation failed"
            )

        return state

    def _classify_severity(self, score: float) -> Literal['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
        """Classify risk severity based on score"""
        if score >= self.severity_thresholds['CRITICAL']:
            return 'CRITICAL'
        elif score >= self.severity_thresholds['HIGH']:
            return 'HIGH'
        elif score >= self.severity_thresholds['MEDIUM']:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _format_result(self, state: RiskAgentState) -> AgentResult:
        """Format workflow state into AgentResult"""
        assessment = state.get('risk_assessment')
        alert = state.get('alert_recommendation')

        # Build insights
        insights = []
        if assessment:
            insights.append(f"## Overall Risk Assessment: **{assessment.overall_severity}** (Score: {assessment.overall_score:.2f})")
            insights.append(f"\n### Top Risks:")
            insights.extend([f"- {risk}" for risk in assessment.top_risks])

            insights.append(f"\n### Risk Breakdown:")
            for risk_score in assessment.risk_scores:
                insights.append(f"- **{risk_score.category.title()}**: {risk_score.severity} ({risk_score.score:.2f})")

        # Build recommendations
        recommendations = []
        if assessment:
            recommendations.extend(assessment.recommended_actions)

        if alert and alert.should_alert:
            recommendations.append(f"**ALERT**: {alert.message}")

        # Build metrics
        metrics = {
            "overall_risk_score": assessment.overall_score if assessment else 0.0,
            "overall_severity": assessment.overall_severity if assessment else "UNKNOWN",
            "delivery_risk": state.get('delivery_data', {}).get('risk_score', 0.0),
            "inventory_risk": state.get('inventory_data', {}).get('risk_score', 0.0),
            "quality_risk": state.get('quality_data', {}).get('risk_score', 0.0),
            "financial_risk": state.get('financial_data', {}).get('risk_score', 0.0),
            "alert_severity": alert.severity if alert else None,
            "should_alert": alert.should_alert if alert else False
        }

        return AgentResult(
            agent_name=self.name,
            query=state['user_query'],
            timestamp=datetime.utcnow(),
            success=not bool(state.get('error')),
            insights=insights,
            metrics=metrics,
            recommendations=recommendations
        )
