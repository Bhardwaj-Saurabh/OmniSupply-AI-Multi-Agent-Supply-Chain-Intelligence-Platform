"""
Supervisor Agent for OmniSupply platform.
Orchestrates multiple specialized agents to fulfill complex queries.
"""

from typing import Dict, Any, List, Optional, TypedDict, Literal
from datetime import datetime
import asyncio
import logging
import os
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from opik import track
from opik.integrations.langchain import OpikTracer

from ..agents.base import BaseAgent, AgentRegistry
from ..data.models import AgentResult

logger = logging.getLogger(__name__)

# Get Opik project name from environment
OPIK_PROJECT_NAME = os.getenv("OPIK_PROJECT_NAME", "omnisupply")


# Pydantic models for structured outputs

class AgentSelection(BaseModel):
    """LLM-structured output for agent routing"""
    agents: List[str] = Field(description="List of agent names to invoke")
    reasoning: str = Field(description="Why these agents were selected")
    execution_order: Literal['parallel', 'sequential'] = Field(
        description="How to execute agents"
    )


class TaskPlan(BaseModel):
    """LLM-structured output for task planning"""
    steps: List[str] = Field(description="Step-by-step plan")
    agents_needed: List[str] = Field(description="Agents required")
    expected_output: str = Field(description="What the final output should contain")


class KPIItem(BaseModel):
    """Individual KPI"""
    name: str
    value: str  # String to allow any format (numbers, percentages, etc.)

class ExecutiveSummary(BaseModel):
    """LLM-structured output for final report"""
    summary: str = Field(description="2-3 paragraph executive summary")
    key_insights: List[str] = Field(description="3-5 key insights")
    recommendations: List[str] = Field(description="Top 3 recommended actions")
    kpis: List[KPIItem] = Field(description="Key performance indicators as list")


# Supervisor state

class SupervisorState(TypedDict):
    """State for supervisor agent"""
    session_id: str
    user_query: str
    context: Dict[str, Any]
    task_plan: Optional[TaskPlan]
    selected_agents: List[str]
    agent_results: Dict[str, AgentResult]
    final_report: Optional[str]
    executive_summary: Optional[ExecutiveSummary]
    error: Optional[str]


class SupervisorAgent:
    """
    Supervisor agent that orchestrates multiple specialized agents.

    Workflow:
    1. Parse Query → Understand user intent
    2. Plan Task → Break down into steps
    3. Select Agents → Choose which agents to invoke
    4. Execute Agents → Run agents (parallel or sequential)
    5. Aggregate Results → Combine insights
    6. Generate Report → Create final output
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        llm: Optional[ChatOpenAI] = None
    ):
        """
        Initialize supervisor agent.

        Args:
            agent_registry: Registry of available agents
            llm: Language model for orchestration
        """
        self.registry = agent_registry
        self.llm = llm or ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            callbacks=[OpikTracer(project_name=OPIK_PROJECT_NAME)]
        )

        # LLMs with structured outputs
        self.llm_router = self.llm.with_structured_output(AgentSelection)
        self.llm_planner = self.llm.with_structured_output(TaskPlan)
        self.llm_summarizer = self.llm.with_structured_output(ExecutiveSummary)

        # Build workflow
        self.graph = self._build_graph()

        logger.info(f"✅ Supervisor agent initialized with {len(self.registry)} agents")

    def _build_graph(self) -> StateGraph:
        """Build supervisor workflow"""
        workflow = StateGraph(SupervisorState)

        # Add nodes
        workflow.add_node("parse_query", self.parse_query_node)
        workflow.add_node("plan_task", self.plan_task_node)
        workflow.add_node("select_agents", self.select_agents_node)
        workflow.add_node("execute_agents", self.execute_agents_node)
        workflow.add_node("aggregate_results", self.aggregate_results_node)
        workflow.add_node("generate_report", self.generate_report_node)

        # Define flow
        workflow.set_entry_point("parse_query")
        workflow.add_edge("parse_query", "plan_task")
        workflow.add_edge("plan_task", "select_agents")
        workflow.add_edge("select_agents", "execute_agents")
        workflow.add_edge("execute_agents", "aggregate_results")
        workflow.add_edge("aggregate_results", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    # Node implementations

    def parse_query_node(self, state: SupervisorState) -> SupervisorState:
        """Parse and understand user query"""
        logger.info(f"📋 Parsing query: {state['user_query'][:100]}")

        # Add basic context
        state['context']['timestamp'] = datetime.now().isoformat()
        state['context']['available_agents'] = self.registry.list_agents()

        return state

    def plan_task_node(self, state: SupervisorState) -> SupervisorState:
        """Create execution plan"""
        logger.info("📝 Planning task...")

        prompt = f"""You are a task planning AI for a supply chain intelligence platform.

Available agents:
{self._format_agent_capabilities()}

User query: {state['user_query']}

Create a step-by-step plan to fulfill this query. Determine:
1. What steps are needed
2. Which agents should be involved
3. What the final output should contain

Be specific and actionable.
"""

        try:
            task_plan: TaskPlan = self.llm_planner.invoke(prompt)
            state['task_plan'] = task_plan

            logger.info(f"  Plan created: {len(task_plan.steps)} steps")
            for i, step in enumerate(task_plan.steps, 1):
                logger.info(f"    {i}. {step}")

        except Exception as e:
            logger.error(f"Planning failed: {e}")
            state['error'] = f"Planning failed: {e}"

        return state

    def select_agents_node(self, state: SupervisorState) -> SupervisorState:
        """Select which agents to invoke"""
        logger.info("🎯 Selecting agents...")

        prompt = f"""You are an agent router for a supply chain intelligence platform.

Available agents and their capabilities:
{self._format_agent_capabilities()}

User query: {state['user_query']}

Task plan: {state['task_plan'].steps if state.get('task_plan') else 'No plan'}

Select which agents to invoke. Return:
- agents: List of agent names (e.g., ["data_analyst", "risk_agent"])
- reasoning: Why these agents
- execution_order: "parallel" (independent) or "sequential" (dependent)

Choose minimal necessary agents.
"""

        try:
            selection: AgentSelection = self.llm_router.invoke(prompt)

            # Validate agent names
            valid_agents = [
                a for a in selection.agents
                if a in self.registry.list_agents()
            ]

            if not valid_agents:
                logger.warning("No valid agents selected, using best match")
                best_agent = self.registry.find_best_agent(state['user_query'])
                valid_agents = [best_agent.name] if best_agent else []

            state['selected_agents'] = valid_agents

            logger.info(f"  Selected {len(valid_agents)} agents: {valid_agents}")
            logger.info(f"  Reasoning: {selection.reasoning}")
            logger.info(f"  Execution: {selection.execution_order}")

            state['context']['execution_order'] = selection.execution_order

        except Exception as e:
            logger.error(f"Agent selection failed: {e}")
            state['error'] = f"Agent selection failed: {e}"

        return state

    def execute_agents_node(self, state: SupervisorState) -> SupervisorState:
        """Execute selected agents"""
        logger.info("🚀 Executing agents...")

        if not state['selected_agents']:
            logger.warning("No agents to execute")
            return state

        execution_order = state['context'].get('execution_order', 'parallel')

        try:
            if execution_order == 'parallel':
                # Run agents in parallel
                results = asyncio.run(self._execute_parallel(
                    state['selected_agents'],
                    state['user_query'],
                    state['context']
                ))
            else:
                # Run agents sequentially
                results = self._execute_sequential(
                    state['selected_agents'],
                    state['user_query'],
                    state['context']
                )

            state['agent_results'] = results

            # Log results
            for agent_name, result in results.items():
                status = "✅" if result.success else "❌"
                logger.info(f"  {status} {agent_name}: {len(result.insights)} insights")

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            state['error'] = f"Agent execution failed: {e}"

        return state

    async def _execute_parallel(
        self,
        agent_names: List[str],
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, AgentResult]:
        """Execute agents in parallel"""
        logger.info(f"  Running {len(agent_names)} agents in parallel...")

        tasks = []
        for agent_name in agent_names:
            agent = self.registry.get_agent(agent_name)
            if agent:
                # Create async task
                task = asyncio.to_thread(agent.execute, query, context)
                tasks.append((agent_name, task))

        # Wait for all to complete
        results = {}
        for agent_name, task in tasks:
            try:
                result = await task
                results[agent_name] = result
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                results[agent_name] = AgentResult(
                    agent_name=agent_name,
                    query=query,
                    timestamp=datetime.now(),
                    success=False,
                    error=str(e)
                )

        return results

    def _execute_sequential(
        self,
        agent_names: List[str],
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, AgentResult]:
        """Execute agents sequentially"""
        logger.info(f"  Running {len(agent_names)} agents sequentially...")

        results = {}
        accumulated_context = context.copy()

        for agent_name in agent_names:
            agent = self.registry.get_agent(agent_name)
            if not agent:
                logger.warning(f"Agent {agent_name} not found")
                continue

            try:
                # Execute with accumulated context
                result = agent.execute(query, accumulated_context)
                results[agent_name] = result

                # Pass results to next agent
                accumulated_context[f'{agent_name}_result'] = result

            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                results[agent_name] = AgentResult(
                    agent_name=agent_name,
                    query=query,
                    timestamp=datetime.now(),
                    success=False,
                    error=str(e)
                )

        return results

    def aggregate_results_node(self, state: SupervisorState) -> SupervisorState:
        """Aggregate results from all agents"""
        logger.info("📊 Aggregating results...")

        if not state['agent_results']:
            logger.warning("No results to aggregate")
            return state

        # Collect all insights and metrics
        all_insights = []
        all_recommendations = []
        all_metrics = {}

        for agent_name, result in state['agent_results'].items():
            if result.success:
                all_insights.extend(result.insights)
                all_recommendations.extend(result.recommendations)
                all_metrics[agent_name] = result.metrics

        logger.info(f"  Total insights: {len(all_insights)}")
        logger.info(f"  Total recommendations: {len(all_recommendations)}")

        state['context']['aggregated_insights'] = all_insights
        state['context']['aggregated_recommendations'] = all_recommendations
        state['context']['aggregated_metrics'] = all_metrics

        return state

    def generate_report_node(self, state: SupervisorState) -> SupervisorState:
        """Generate final executive report"""
        logger.info("📄 Generating report...")

        if not state['agent_results']:
            state['final_report'] = "No results available to generate report."
            return state

        # Build context for LLM
        results_summary = self._format_results_for_llm(state['agent_results'])

        prompt = f"""You are an executive report writer for OmniSupply platform.

User query: {state['user_query']}

Agent results:
{results_summary}

Create an executive summary with:
1. summary: 2-3 paragraphs covering key findings
2. key_insights: 3-5 most important insights
3. recommendations: Top 3 priority actions
4. kpis: Key metrics from the analysis

Make it executive-friendly: clear, concise, actionable.
"""

        try:
            exec_summary: ExecutiveSummary = self.llm_summarizer.invoke(prompt)
            state['executive_summary'] = exec_summary

            # Build final report
            report = self._build_report(state, exec_summary)
            state['final_report'] = report

            logger.info("  ✅ Report generated")

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            state['error'] = f"Report generation failed: {e}"
            state['final_report'] = f"Error generating report: {e}"

        return state

    def _format_agent_capabilities(self) -> str:
        """Format agent capabilities for LLM"""
        lines = []
        for agent_name in self.registry.list_agents():
            agent = self.registry.get_agent(agent_name)
            if agent:
                caps = agent.get_capabilities()
                lines.append(f"- {agent_name}: {', '.join(caps)}")
        return "\n".join(lines)

    def _format_results_for_llm(self, results: Dict[str, AgentResult]) -> str:
        """Format agent results for LLM consumption"""
        lines = []
        for agent_name, result in results.items():
            lines.append(f"\n**{agent_name}**:")
            if result.success:
                lines.append(f"  Insights: {len(result.insights)}")
                for insight in result.insights[:3]:  # Show top 3
                    lines.append(f"    - {insight}")
                if result.recommendations:
                    lines.append(f"  Recommendations: {len(result.recommendations)}")
                    for rec in result.recommendations[:2]:
                        lines.append(f"    - {rec}")
            else:
                lines.append(f"  Error: {result.error}")
        return "\n".join(lines)

    def _build_report(self, state: SupervisorState, summary: ExecutiveSummary) -> str:
        """Build final markdown report"""
        report = f"""# OmniSupply Intelligence Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Query:** {state['user_query']}
**Agents Used:** {', '.join(state['selected_agents'])}

---

## Executive Summary

{summary.summary}

---

## Key Insights

"""
        for i, insight in enumerate(summary.key_insights, 1):
            report += f"{i}. {insight}\n"

        report += "\n---\n\n## Recommended Actions\n\n"

        for i, rec in enumerate(summary.recommendations, 1):
            report += f"{i}. {rec}\n"

        report += "\n---\n\n## Key Performance Indicators\n\n"

        # KPIs is now a list of KPIItem objects
        for kpi_item in summary.kpis:
            report += f"- **{kpi_item.name}**: {kpi_item.value}\n"

        report += "\n---\n\n## Detailed Results by Agent\n\n"

        for agent_name, result in state['agent_results'].items():
            report += f"### {agent_name}\n\n"
            if result.success:
                if result.insights:
                    report += "**Insights:**\n"
                    for insight in result.insights:
                        report += f"- {insight}\n"
                if result.metrics:
                    report += "\n**Metrics:**\n"
                    for k, v in result.metrics.items():
                        report += f"- {k}: {v}\n"
            else:
                report += f"*Error: {result.error}*\n"
            report += "\n"

        return report

    @track(project_name=OPIK_PROJECT_NAME)
    def execute(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute supervisor workflow.

        Args:
            query: User query
            context: Additional context

        Returns:
            Dict with final_report, executive_summary, agent_results
        """
        logger.info(f"🎯 Supervisor executing: {query}")

        initial_state = {
            "session_id": f"supervisor_{datetime.now().timestamp()}",
            "user_query": query,
            "context": context or {},
            "task_plan": None,
            "selected_agents": [],
            "agent_results": {},
            "final_report": None,
            "executive_summary": None,
            "error": None
        }

        result = self.graph.invoke(initial_state, config={"callbacks": [OpikTracer(project_name=OPIK_PROJECT_NAME)]})

        logger.info("✅ Supervisor execution complete")

        return result
