"""Email/Workflow Agent - Alert generation, task creation, and stakeholder notifications"""

from typing import Optional, Dict, Any, List, TypedDict, Literal
from datetime import datetime
import logging

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field, EmailStr
from opik.integrations.langchain import OpikTracer

from .base import BaseAgent
from ..data.models import AgentResult
from ..storage.sql.database import DatabaseClient
from ..storage.vector.chromadb_client import OmniSupplyVectorStore

logger = logging.getLogger(__name__)


# Pydantic models for structured outputs
class Stakeholder(BaseModel):
    """Stakeholder information"""
    name: str
    role: str
    email: EmailStr
    notification_level: Literal['all', 'critical_only', 'digest']


class Alert(BaseModel):
    """Alert notification"""
    alert_id: str = Field(description="Unique alert ID")
    severity: Literal['INFO', 'WARNING', 'CRITICAL']
    title: str = Field(description="Alert title")
    message: str = Field(description="Alert message body")
    affected_area: str = Field(description="Affected business area (e.g., 'supply chain', 'finance')")
    stakeholders: List[str] = Field(description="Stakeholder roles to notify")
    recommended_action: Optional[str] = Field(default=None, description="Recommended action")


class Task(BaseModel):
    """Task to be created"""
    task_id: str = Field(description="Unique task ID")
    title: str = Field(description="Task title")
    description: str = Field(description="Task description")
    priority: Literal['HIGH', 'MEDIUM', 'LOW']
    assignee: str = Field(description="Assigned role/team")
    due_date: str = Field(description="Due date")
    tags: List[str] = Field(default_factory=list, description="Task tags")


class EmailMessage(BaseModel):
    """Email message to be sent"""
    to: List[EmailStr] = Field(description="Recipients")
    cc: List[EmailStr] = Field(default_factory=list, description="CC recipients")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body (markdown format)")
    priority: Literal['HIGH', 'NORMAL', 'LOW']


class MeetingAgenda(BaseModel):
    """Meeting agenda"""
    meeting_title: str
    date: str
    duration: str = Field(description="Duration (e.g., '1 hour')")
    attendees: List[str] = Field(description="Required attendees (roles)")
    agenda_items: List[str] = Field(description="Agenda topics")
    discussion_points: List[str] = Field(description="Key discussion points")
    preparation_required: List[str] = Field(default_factory=list, description="Prep work needed")


# State for Email Agent workflow
class EmailAgentState(TypedDict):
    """State passed between nodes"""
    user_query: str
    workflow_type: Literal['alert', 'task', 'email', 'meeting_agenda']
    alerts: Optional[List[Alert]]
    tasks: Optional[List[Task]]
    emails: Optional[List[EmailMessage]]
    meeting_agenda: Optional[MeetingAgenda]
    stakeholders: Optional[List[Stakeholder]]
    error: Optional[str]


class EmailAgent(BaseAgent):
    """
    Email/Workflow Agent for alerts, tasks, and stakeholder communications.

    Capabilities:
    - Alert generation and prioritization
    - Task creation with assignments
    - Email notification drafting
    - Meeting agenda preparation
    - Stakeholder management
    """

    # Predefined stakeholders (in production, load from database)
    DEFAULT_STAKEHOLDERS = [
        Stakeholder(
            name="Sarah Chen",
            role="VP Operations",
            email="sarah.chen@omnisupply.com",
            notification_level="all"
        ),
        Stakeholder(
            name="Michael Torres",
            role="CFO",
            email="michael.torres@omnisupply.com",
            notification_level="critical_only"
        ),
        Stakeholder(
            name="Jessica Park",
            role="Supply Chain Manager",
            email="jessica.park@omnisupply.com",
            notification_level="all"
        ),
        Stakeholder(
            name="David Kim",
            role="Data Analyst",
            email="david.kim@omnisupply.com",
            notification_level="digest"
        ),
        Stakeholder(
            name="Emily Rodriguez",
            role="CEO",
            email="emily.rodriguez@omnisupply.com",
            notification_level="critical_only"
        )
    ]

    def __init__(
        self,
        db_client: DatabaseClient,
        vector_store: Optional[OmniSupplyVectorStore] = None,
        llm: Optional[ChatOpenAI] = None
    ):
        """Initialize Email Agent"""
        # Initialize LLMs for structured outputs
        base_llm = llm or ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            callbacks=[OpikTracer()]
        )

        self.llm_alert = base_llm.with_structured_output(Alert)
        self.llm_task = base_llm.with_structured_output(Task)
        self.llm_email = base_llm.with_structured_output(EmailMessage)
        self.llm_agenda = base_llm.with_structured_output(MeetingAgenda)

        super().__init__(
            name="email_agent",
            llm=base_llm,
            db_client=db_client,
            vector_store=vector_store
        )

    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for email/workflow automation"""
        workflow = StateGraph(EmailAgentState)

        # Add nodes
        workflow.add_node("classify_workflow", self.classify_workflow_node)
        workflow.add_node("load_stakeholders", self.load_stakeholders_node)
        workflow.add_node("generate_alerts", self.generate_alerts_node)
        workflow.add_node("create_tasks", self.create_tasks_node)
        workflow.add_node("draft_emails", self.draft_emails_node)

        # Define edges
        workflow.set_entry_point("classify_workflow")
        workflow.add_edge("classify_workflow", "load_stakeholders")

        # Conditional routing based on workflow type
        workflow.add_conditional_edges(
            "load_stakeholders",
            self._route_workflow,
            {
                "alert": "generate_alerts",
                "task": "create_tasks",
                "email": "draft_emails",
                "meeting": "draft_emails"  # For now, all workflows lead to email draft
            }
        )

        workflow.add_edge("generate_alerts", "draft_emails")
        workflow.add_edge("create_tasks", "draft_emails")
        workflow.add_edge("draft_emails", END)

        return workflow.compile()

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "Alert generation and prioritization",
            "Task creation with assignments",
            "Email notification drafting",
            "Meeting agenda preparation",
            "Stakeholder management",
            "Workflow automation"
        ]

    def can_handle(self, query: str) -> float:
        """Determine if this agent can handle the query (0-1 confidence)"""
        query_lower = query.lower()

        # High confidence keywords
        high_confidence = ["alert", "notify", "email", "send", "task", "meeting", "agenda"]
        # Medium confidence keywords
        medium_confidence = ["stakeholder", "notification", "inform", "schedule", "assign"]

        score = 0.0
        for keyword in high_confidence:
            if keyword in query_lower:
                score += 0.15

        for keyword in medium_confidence:
            if keyword in query_lower:
                score += 0.08

        return min(score, 1.0)

    # ===== Node Functions =====

    def classify_workflow_node(self, state: EmailAgentState) -> EmailAgentState:
        """Classify the type of workflow needed"""
        logger.info("[Email Agent] Classifying workflow type")

        query_lower = state['user_query'].lower()

        # Simple keyword-based classification
        if any(word in query_lower for word in ['alert', 'notify', 'warn']):
            workflow_type = 'alert'
        elif any(word in query_lower for word in ['task', 'assign', 'create task']):
            workflow_type = 'task'
        elif any(word in query_lower for word in ['meeting', 'agenda']):
            workflow_type = 'meeting_agenda'
        else:
            # Default to email
            workflow_type = 'email'

        state['workflow_type'] = workflow_type
        logger.info(f"[Email Agent] Workflow type: {workflow_type}")

        return state

    def load_stakeholders_node(self, state: EmailAgentState) -> EmailAgentState:
        """Load stakeholder information"""
        logger.info("[Email Agent] Loading stakeholders")

        # In production, load from database
        # For now, use default stakeholders
        state['stakeholders'] = self.DEFAULT_STAKEHOLDERS

        logger.info(f"[Email Agent] Loaded {len(self.DEFAULT_STAKEHOLDERS)} stakeholders")

        return state

    def _route_workflow(self, state: EmailAgentState) -> str:
        """Route based on workflow type"""
        workflow_type = state['workflow_type']

        if workflow_type == 'alert':
            return 'alert'
        elif workflow_type == 'task':
            return 'task'
        elif workflow_type == 'meeting_agenda':
            return 'meeting'
        else:
            return 'email'

    def generate_alerts_node(self, state: EmailAgentState) -> EmailAgentState:
        """Generate alerts based on query"""
        logger.info("[Email Agent] Generating alerts")

        prompt = f"""Generate supply chain alerts based on this request.

User Request: {state['user_query']}

Available stakeholder roles:
{', '.join([s.role for s in state.get('stakeholders', [])])}

Create alerts with:
1. Unique alert ID
2. Severity (INFO, WARNING, CRITICAL)
3. Title and message
4. Affected business area
5. Which stakeholder roles to notify
6. Recommended action

Generate 1-3 relevant alerts.
"""

        alerts = []
        try:
            # Generate multiple alerts if needed
            for i in range(3):  # Max 3 alerts
                try:
                    alert: Alert = self.llm_alert.invoke(prompt)
                    alert.alert_id = f"ALERT-{datetime.utcnow().strftime('%Y%m%d')}-{i+1:03d}"
                    alerts.append(alert)

                    # If query mentions specific alert, stop after one
                    if i == 0 and not any(word in state['user_query'].lower() for word in ['all', 'multiple', 'several']):
                        break
                except Exception:
                    break

            state['alerts'] = alerts
            logger.info(f"[Email Agent] Generated {len(alerts)} alerts")

        except Exception as e:
            logger.error(f"[Email Agent] Alert generation error: {e}")
            state['error'] = f"Alert generation failed: {str(e)}"

        return state

    def create_tasks_node(self, state: EmailAgentState) -> EmailAgentState:
        """Create tasks based on query"""
        logger.info("[Email Agent] Creating tasks")

        prompt = f"""Create actionable tasks based on this request.

User Request: {state['user_query']}

Available teams/roles for assignment:
{', '.join([s.role for s in state.get('stakeholders', [])])}

Create tasks with:
1. Unique task ID
2. Title and description
3. Priority (HIGH, MEDIUM, LOW)
4. Assignee (role/team)
5. Due date
6. Relevant tags

Generate 1-5 tasks.
"""

        tasks = []
        try:
            # Generate multiple tasks if needed
            for i in range(5):  # Max 5 tasks
                try:
                    task: Task = self.llm_task.invoke(prompt)
                    task.task_id = f"TASK-{datetime.utcnow().strftime('%Y%m%d')}-{i+1:03d}"
                    tasks.append(task)

                    # Stop if only one task mentioned
                    if i == 0 and not any(word in state['user_query'].lower() for word in ['all', 'multiple', 'several']):
                        break
                except Exception:
                    break

            state['tasks'] = tasks
            logger.info(f"[Email Agent] Created {len(tasks)} tasks")

        except Exception as e:
            logger.error(f"[Email Agent] Task creation error: {e}")
            if not state.get('error'):
                state['error'] = f"Task creation failed: {str(e)}"

        return state

    def draft_emails_node(self, state: EmailAgentState) -> EmailAgentState:
        """Draft email notifications"""
        logger.info("[Email Agent] Drafting emails")

        workflow_type = state['workflow_type']
        stakeholders = state.get('stakeholders', [])
        alerts = state.get('alerts', [])
        tasks = state.get('tasks', [])

        # Build email content based on workflow type
        if workflow_type == 'alert' and alerts:
            # Draft emails for alerts
            emails = []
            for alert in alerts:
                # Determine recipients based on alert severity and stakeholder preferences
                recipients = []
                for stakeholder in stakeholders:
                    if stakeholder.role in alert.stakeholders:
                        if alert.severity == 'CRITICAL' or stakeholder.notification_level == 'all':
                            recipients.append(stakeholder.email)

                if recipients:
                    prompt = f"""Draft an email notification for this alert.

Alert:
- ID: {alert.alert_id}
- Severity: {alert.severity}
- Title: {alert.title}
- Message: {alert.message}
- Affected Area: {alert.affected_area}
- Recommended Action: {alert.recommended_action}

Recipients: {', '.join([str(r) for r in recipients])}

Create a professional email with:
1. Clear subject line
2. Concise body in markdown format
3. Call to action
4. Appropriate priority
"""

                    try:
                        email: EmailMessage = self.llm_email.invoke(prompt)
                        email.to = recipients
                        emails.append(email)
                    except Exception as e:
                        logger.error(f"[Email Agent] Email draft error: {e}")

            state['emails'] = emails
            logger.info(f"[Email Agent] Drafted {len(emails)} alert emails")

        elif workflow_type == 'task' and tasks:
            # Draft emails for task assignments
            emails = []
            for task in tasks:
                # Find assignee email
                assignee_email = None
                for stakeholder in stakeholders:
                    if stakeholder.role == task.assignee:
                        assignee_email = stakeholder.email
                        break

                if assignee_email:
                    prompt = f"""Draft a task assignment email.

Task:
- ID: {task.task_id}
- Title: {task.title}
- Description: {task.description}
- Priority: {task.priority}
- Due Date: {task.due_date}
- Tags: {', '.join(task.tags)}

Recipient: {assignee_email}

Create a professional email with task details and expectations.
"""

                    try:
                        email: EmailMessage = self.llm_email.invoke(prompt)
                        email.to = [assignee_email]
                        emails.append(email)
                    except Exception as e:
                        logger.error(f"[Email Agent] Email draft error: {e}")

            state['emails'] = emails
            logger.info(f"[Email Agent] Drafted {len(emails)} task emails")

        else:
            # General email draft
            prompt = f"""Draft an email based on this request.

User Request: {state['user_query']}

Available recipients:
{chr(10).join([f"- {s.name} ({s.role}): {s.email}" for s in stakeholders])}

Create a professional email with appropriate subject and body.
"""

            try:
                email: EmailMessage = self.llm_email.invoke(prompt)
                state['emails'] = [email]
                logger.info("[Email Agent] Drafted general email")
            except Exception as e:
                logger.error(f"[Email Agent] Email draft error: {e}")
                if not state.get('error'):
                    state['error'] = f"Email draft failed: {str(e)}"

        return state

    def _format_result(self, state: EmailAgentState) -> AgentResult:
        """Format workflow state into AgentResult"""
        workflow_type = state['workflow_type']
        alerts = state.get('alerts', [])
        tasks = state.get('tasks', [])
        emails = state.get('emails', [])

        # Build insights
        insights = []

        if workflow_type == 'alert' and alerts:
            insights.append(f"## Generated {len(alerts)} Alert(s)")
            for alert in alerts:
                insights.append(f"\n### {alert.title} ({alert.severity})")
                insights.append(f"- **ID**: {alert.alert_id}")
                insights.append(f"- **Message**: {alert.message}")
                insights.append(f"- **Affected Area**: {alert.affected_area}")
                if alert.recommended_action:
                    insights.append(f"- **Action**: {alert.recommended_action}")

        if workflow_type == 'task' and tasks:
            insights.append(f"## Created {len(tasks)} Task(s)")
            for task in tasks:
                insights.append(f"\n### {task.title} ({task.priority})")
                insights.append(f"- **ID**: {task.task_id}")
                insights.append(f"- **Assignee**: {task.assignee}")
                insights.append(f"- **Due**: {task.due_date}")
                insights.append(f"- **Description**: {task.description}")

        if emails:
            insights.append(f"\n## Drafted {len(emails)} Email(s)")
            for email in emails:
                insights.append(f"\n### To: {', '.join([str(e) for e in email.to])}")
                insights.append(f"- **Subject**: {email.subject}")
                insights.append(f"- **Priority**: {email.priority}")
                insights.append(f"\n**Body**:\n{email.body[:200]}...")  # Preview

        # Build recommendations
        recommendations = []
        if alerts:
            for alert in alerts:
                if alert.recommended_action:
                    recommendations.append(f"[{alert.severity}] {alert.recommended_action}")

        if tasks:
            recommendations.append(f"Review and confirm {len(tasks)} task assignments")

        # Build metrics
        metrics = {
            "workflow_type": workflow_type,
            "alerts_generated": len(alerts),
            "tasks_created": len(tasks),
            "emails_drafted": len(emails),
            "stakeholders_notified": len(set([str(e) for email in emails for e in email.to]))
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
            raw_data={
                'alerts': [a.model_dump() for a in alerts] if alerts else [],
                'tasks': [t.model_dump() for t in tasks] if tasks else [],
                'emails': [e.model_dump() for e in emails] if emails else []
            }
        )
