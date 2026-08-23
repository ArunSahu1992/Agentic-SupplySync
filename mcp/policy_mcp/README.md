# SupplySync — Pharmaceutical Policy RAG + Policy MCP Server

This is a synthetic demo implementation for the Gemini Enterprise / Gemini ADK SupplySync hackathon architecture.

## Architecture

Gemini Enterprise / ADK Agent
        |
        v
   Policy MCP Server
        |
        +---- search_policy
        |
        +---- evaluate_supply_decision
        |
        v
  Policy RAG Engine
        |
        +---- Gemini Embeddings
        +---- ChromaDB
        +---- Pharmaceutical Policy / SOP / Contract documents

The MCP server is a governance boundary. It does not execute ERP or supplier actions.
It returns the policy evidence, recommended action, approval requirement, confidence, and source chunk IDs.

## Setup

1. Create a virtual environment.
2. Install requirements.
3. Copy `.env.example` to `.env` and add `GEMINI_API_KEY`.
4. Run `python ingest.py`.
5. Run `python test_policy.py`.
6. Run the MCP server with `python policy_mcp_server.py`.

## ADK / Gemini Enterprise integration

For ADK, launch the MCP server over stdio using an MCPToolset and StdioServerParameters, for example:

from google.adk.tools.mcp_tool import MCPToolset, StdioServerParameters

policy_tools = MCPToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=["policy_mcp_server.py"],
    )
)

Then expose `policy_tools` to the Concierge/Resolution agent.

## Important governance behavior

A policy recommendation is not the same as execution authorization.

Safe flow:
Policy MCP -> recommended action -> approval check -> Action Executor -> audit log

If `requires_approval=true`, the workflow should persist as WAITING_FOR_APPROVAL. Gemini Enterprise can present the approval interaction. Once approved, the workflow resumes and calls the Action Executor with the approval reference.
