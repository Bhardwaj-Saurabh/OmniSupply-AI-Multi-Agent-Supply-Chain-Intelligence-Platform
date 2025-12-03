# Meeting/Report Agent - Architecture

## Purpose
Synthesizes insights from Data Analyst, Risk, and Finance agents into executive-ready reports and meeting materials.

## Core Capabilities

1. **Weekly Reports** - Automated supply chain + finance summaries
2. **CxO Summaries** - Executive-level insights (3-5 min read)
3. **Action Recommendations** - Top 3 priority actions with impact

## Architecture

```
Meeting/Report Agent
├── Query Parser → Classify report type
├── Data Aggregator → Collect from other agents
├── Report Generator → Create structured reports
├── Summary Generator → CxO-level summaries
├── Action Recommender → Top 3 actions
└── Formatter → PDF/Markdown/Email output
```

## State Schema

```python
class ReportAgentState(TypedDict):
    report_type: Literal['weekly', 'monthly', 'executive', 'meeting_prep']
    time_period: TimePeriod
    data_sources: Dict[str, Any]  # From other agents
    report: Report
    cxo_summary: CxOSummary
    recommendations: List[Action]
    output_format: Literal['markdown', 'pdf', 'email']
```

## Key Nodes

1. **Data Aggregator**: Queries Data Analyst, Risk, Finance agents
2. **Report Generator**: Structures weekly/monthly reports
3. **CxO Summary**: 3-5 min executive brief
4. **Action Recommender**: Top 3 priorities with ROI

## Outputs

- **Weekly Report**: Operations + Finance + Risks (2-3 pages)
- **CxO Summary**: Key metrics + trends + actions (1 page)
- **Meeting Agenda**: Pre-populated with insights
