# SupplySync

SupplySync is a supply chain resilience platform designed to coordinate disruption response, impact analysis, approvals, and supplier actions through a set of specialized agents and MCP integrations.

## Repository structure

- `frontend/angular/` – Angular application modules for dashboard, disruptions, orders, approvals, policies, MCP monitoring, agent trace, audit, and chat.
- `backend/` – API, database, models, services, and notifications for core backend logic.
- `agents/` – orchestration and domain-specific AI agents.
- `mcp/` – Model Context Protocol integrations for suppliers, ERP, policy, and action workflows.
- `rag/` – ingestion, embedding, retrieval, and policy vector store components.
- `mock_systems/` – mock supplier, ERP, and OMS API services.
- `data/` – SQLite database and seed/policy data.
- `tests/` – automated test suites.
- `docker/` – container configuration.
- `.github/workflows/` – CI/CD automation.

## Target architecture

- Frontend: Angular dashboards and workflow UIs.
- Backend: FastAPI/REST services for orchestration and data access.
- Agent layer: orchestrator plus disruption, impact, and concierge agents.
- MCP layer: external system connectors and action execution endpoints.
- RAG layer: policy and document retrieval for compliance-aware decisions.
- Data: SQLite-backed storage with seeded reference data.

## Getting started

1. Create and activate a Python virtual environment.
2. Install backend dependencies.
3. Install frontend dependencies in the Angular app.
4. Start the backend API and frontend app.
5. Seed local data and run tests.

## Notes

This repository is intentionally scaffolded as a working project skeleton. The application modules can be expanded progressively as the platform is implemented.
