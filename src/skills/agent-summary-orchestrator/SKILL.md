---
name: agent-summary-orchestrator
description: Agent summary protocol for orchestrator with telemetry and cost tracking
---

# Agent Summary Protocol - Orchestrator

Orchestrator reads agent summaries and tracks costs across workflow execution.

## File Structure

**Two separate files for clean separation:**

| File | Purpose |
|------|---------|
| `agent_summaries.jsonl` | Agent work outputs (deliverables, handoff, concerns) |
| `agent_summaries_telemetry.jsonl` | Cost tracking (baseline, cost_summary entries) |

## Telemetry File Schema

```jsonl
{"type":"baseline","session_id":"<epic-planner-session>","completed_at":"2026-01-27T10:00:00-05:00"}
{"type":"cost_summary","baseline":"2026-01-27T10:00:00-05:00","completed_at":"2026-01-27T12:00:00-05:00","total_cost_usd":15.50,"agents":[...]}
```

## How to Calculate Costs

Run `agents-tokens.sh` with the aggregate file:
```bash
agents-tokens.sh --aggregate .scope/{epic_dir}/agent_summaries.jsonl --storeInSummaries
```

This:
1. Reads baseline from `agent_summaries_telemetry.jsonl`
2. Reads agent session IDs from `agent_summaries.jsonl`
3. Calculates costs for each agent
4. Appends `cost_summary` entry to `agent_summaries_telemetry.jsonl`

## Cost Summary Schema

```json
{
  "type": "cost_summary",
  "baseline": "2026-01-27T10:00:00-05:00",
  "completed_at": "2026-01-27T12:00:00-05:00",
  "total_cost_usd": 15.50,
  "agents": [
    {
      "agent": "product-owner",
      "session_id": "30c0069d-7cdb-4840-826d-2ab70bfc48e5",
      "task_id": "1",
      "completed_at": "2026-01-27T10:30:00-05:00",
      "main_cost_usd": 3.50,
      "subagent_cost_usd": 1.20,
      "cost_usd": 4.70,
      "subagents": [...]
    }
  ]
}
```

## Workflow Integration

**At start (/workplan):**
- epic-planner writes baseline to telemetry file
- Sub-planner creates tasks and calls `agents-tokens.sh --storeInSummaries`

**At end (refinement complete):**
- Final aggregation calls `agents-tokens.sh --aggregate --storeInSummaries`
- Final cost summary appended to telemetry file

## Reading Telemetry

```bash
# Get total cost from latest cost_summary
jq -s 'map(select(.type == "cost_summary")) | last | .total_cost_usd' agent_summaries_telemetry.jsonl

# Get per-agent costs
jq -s 'map(select(.type == "cost_summary")) | last | .agents' agent_summaries_telemetry.jsonl
```
