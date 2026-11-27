"""FastMCP server entry point for the Campus Support Companion."""

from fastmcp import FastMCP
from fastmcp.server.auth import StaticTokenVerifier
from starlette.requests import Request
from starlette.responses import JSONResponse

from campus_mcp.config import settings
from campus_mcp.tools import (
    decision_lab,
    escalation_request,
    policy_search,
    resource_finder,
    study_planner,
)

# Optional shared-secret auth. When no token is configured the server is open,
# which keeps local development simple; deployments should always set a token.
auth = (
    StaticTokenVerifier(
        tokens={
            settings.auth_token: {
                "sub": "campo-backend",
                "client_id": "campo-backend",
            }
        }
    )
    if settings.auth_token
    else None
)
mcp = FastMCP("campus-support-companion", auth=auth)

# Register tools
mcp.tool(policy_search.search_policies)
mcp.tool(resource_finder.find_resources)
mcp.tool(study_planner.plan_study)
mcp.tool(decision_lab.evaluate_decision)
mcp.tool(escalation_request.request_escalation)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Readiness probe; intentionally outside the MCP auth boundary."""
    return JSONResponse({"status": "healthy", "service": "campus-mcp"})


def main() -> None:
    """Serve the MCP tools over Streamable HTTP at the configured path."""
    mcp.run(
        transport="http",
        host=settings.host,
        port=settings.port,
        path=settings.path,
        stateless_http=settings.stateless_http,
    )


if __name__ == "__main__":
    main()
