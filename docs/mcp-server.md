# MCP policy and tool server

The MCP server is a separate FastMCP service. The backend calls its tools over the Model Context Protocol, so the tools can be audited, versioned, and reused by other agents (spec Section 10).

## 1. Running it

```bash
cd mcp_server
uv run python -m campus_mcp.server
```

It serves the MCP HTTP transport at `http://127.0.0.1:8001/mcp`. The backend reads this address from `MCP_SERVER_URL`.

## 2. Layout

```
mcp_server/src/campus_mcp/
  server.py                 Creates the FastMCP app, registers tools, starts the server
  tools/
    policy_search.py        search_policies
    resource_finder.py      find_resources
    study_planner.py        plan_study
    decision_lab.py         evaluate_decision
    escalation_request.py   request_escalation
  resources/                Reserved for MCP resources (policy text). Empty.
mcp_server/tests/           Reserved. No tests yet.
```

## 3. Tools

Each tool is a plain Python function with typed inputs and outputs. FastMCP generates the schemas from them.

### search_policies
Searches campus policies by free text and optional category.

| Input | Type | Notes |
|---|---|---|
| `query` | string | Matched against title, summary, and category |
| `category` | string, optional | `mental_health`, `academic_accommodation`, `sexual_harassment`, `financial_aid`, `housing`, `conduct` |
| `limit` | integer, 1 to 20 | Default 5 |

Output: a list of policies with `id`, `title`, `category`, `summary`, `contact_email`, `last_reviewed`.

### find_resources
Returns support services by type, optionally filtered by location and hours.

| Input | Type | Notes |
|---|---|---|
| `resource_type` | string | `counselling`, `health_clinic`, `peer_support`, `emergency`, `legal_aid` |
| `location` | string, optional | Substring match |
| `hours` | string, optional | Substring match |

Output: a list of resources with `name`, `contact`, `hours`, `cost`, `description`.

### plan_study
Builds a simple weekly study plan. Energy level scales the effective hours.

| Input | Type | Notes |
|---|---|---|
| `units` | list of strings | 1 to 20 units |
| `hours_per_week` | integer, 1 to 40 | |
| `energy_level` | `low`, `moderate`, `high` | Multiplies hours by 0.6, 1.0, or 1.3 |
| `exam_weeks_away` | integer, optional | Adds advice when 2 weeks or fewer |

Output: `sessions` (day, time, duration, unit, activity), `total_hours`, `notes`.

### evaluate_decision
Helps compare options against the student's values. It never chooses for the student.

| Input | Type | Notes |
|---|---|---|
| `situation` | string | |
| `options` | list of options | At least 2. Each has `id`, `label`, `pros`, `cons`. |
| `values` | list of strings | What matters most to the student |

Output: `recommended` (the option that best matches the values, or none), `reasoning`, `next_steps`, `crisis_flag`. If the text contains crisis words, `crisis_flag` is true, no recommendation is made, and the response gives emergency contacts.

### request_escalation
Creates an escalation to human support.

| Input | Type | Notes |
|---|---|---|
| `reason` | string | Checked for crisis words |
| `urgency` | `routine`, `urgent`, `crisis` | |
| `preferred_channel` | string, optional | `peer_support` or `security` add contacts |

Output: `ticket_id`, `status`, `estimated_response`, `contacts`, `instructions`, `is_crisis`. Crisis requests get the ticket `CRISIS-IMMEDIATE` and emergency contacts, not a queued ticket.

**Placeholder notice:** these tools use static data and no real case-management system. The escalation tool does not page anyone. The spec requires the escalation tool to be callable only by the safety pipeline, not by the model. That restriction is not enforced yet.

## 4. Data

All catalogues are hard-coded in the tool modules (policies, resources). Replace them with a real source before pilot use. Contact details shown are examples and must be verified with the campus (spec Section 15).

## 5. Adding a tool

1. Create a module in `tools/` with a function that has typed arguments and a docstring. The docstring becomes the tool description.
2. Import the function in `server.py` and register it with `mcp.tool(your_function)`.
3. Call it from the backend through `MCPClient.call_tool("your_function", {...})`. The tool name is the function name.
4. Add a route in `backend/app/api/` if the frontend needs it, and document it in [backend-api.md](backend-api.md).

Run `uv run ruff check .` before committing.
