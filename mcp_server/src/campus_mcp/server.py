"""FastMCP server entry point for the Campus Support Companion."""

from fastmcp import FastMCP

from campus_mcp.tools import (
    decision_lab,
    escalation_request,
    policy_search,
    resource_finder,
    study_planner,
)

mcp = FastMCP("campus-support-companion")

# Register tools
mcp.tool(policy_search.search_policies)
mcp.tool(resource_finder.find_resources)
mcp.tool(study_planner.plan_study)
mcp.tool(decision_lab.evaluate_decision)
mcp.tool(escalation_request.request_escalation)

if __name__ == "__main__":
    mcp.run()
