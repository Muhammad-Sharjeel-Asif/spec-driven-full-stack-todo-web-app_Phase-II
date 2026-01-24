<!-- Sync Impact Report:
Version change: 0.0.0 → 1.0.0
Modified principles: None
Added sections: Security-First Approach, Modularity and Separation of Concerns, Scalability and Performance Optimization, Maintainability and Readability, Frontend Standards, Backend Standards, Database Standards, Authentication Standards, Testing Standards, Code Quality. Constraints, Success Criteria.
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ✅ updated
- .specify/templates/spec-template.md: ✅ updated
- .specify/templates/tasks-template.md: ✅ updated
- .specify/templates/commands/sp.constitution.md: ✅ updated
- .specify/templates/commands/sp.adr.md: ✅ updated
- .specify/templates/commands/sp.analyze.md: ✅ updated
- .specify/templates/commands/sp.checklist.md: ✅ updated
- .specify/templates/commands/sp.clarify.md: ✅ updated
- .specify/templates/commands/sp.implement.md: ✅ updated
- .specify/templates/commands/sp.plan.md: ✅ updated
- .specify/templates/commands/sp.phr.md: ✅ updated
- .specify/templates/commands/sp.reverse-engineer.md: ✅ updated
- .specify/templates/commands/sp.specify.md: ✅ updated
- .specify/templates/commands/sp.taskstoissues.md: ✅ updated
Follow-up TODOs: None
-->
# Phase II Todo Full-Stack Web Application Constitution

## Core Principles

### Security-First Approach
Prioritize security with user data isolation and JWT-based authentication. All operations MUST be filtered by authenticated user ID, ensuring no global data access. If a user is not logged in, they can view the entire website but CANNOT perform any TODO operation.

### Modularity and Separation of Concerns
Maintain clear separation between frontend, backend, and database components to promote independent development and reduce coupling.

### Scalability and Performance Optimization
Design for multi-user environments, ensuring the application is scalable and performs efficiently. API endpoints MUST be secure and responsive. The application MUST pass performance benchmarks (e.g., load times under 2s).

### Maintainability and Readability
Emphasize clean, readable code and comprehensive documentation to facilitate long-term maintenance and onboarding of new developers.

### Frontend Standards
Implement responsive design with Next.js App Router, ensure accessibility (WCAG 2.1 compliance), and adhere to state management best practices. Technology stack: Next.js 16+.

### Backend Standards
Design RESTful APIs with FastAPI, use input validation via Pydantic/SQLModel, and apply async operations where applicable. Technology stack: FastAPI, SQLModel (ORM).

### Database Standards
Utilize a normalized schema in PostgreSQL, employ indexes for frequent queries, and manage migrations with Alembic. Technology stack: Neon Serverless PostgreSQL.

### Authentication Standards
Implement JWT token verification on all endpoints and manage shared secrets securely via environment variables. Technology stack: Better Auth.

### Testing Standards
Achieve a minimum of 80% code coverage with unit tests (Jest for frontend, Pytest for backend) and include integration tests for API flows.

### Code Quality
Enforce TypeScript for frontend, mypy typing for backend, and linting with ESLint/Flake8.

## Constraints

*   Technology stack: Next.js 16+ (frontend), FastAPI (backend), SQLModel (ORM), Neon Serverless PostgreSQL (database), Better Auth (authentication).
*   Multi-user support: All operations filtered by authenticated user ID, no global data access.
*   If user is not logged in, he can view the entire website but cannot perform any TODO operation.
*   Environment: Use .env files for secrets, HTTPS enforcement in production.
*   Deployment: Compatible with Vercel (frontend) and cloud platforms like Render/huggingface (backend).

## Success Criteria

*   All 5 basic Todo features implemented as web app with persistent storage.
*   User authentication and isolation verified through end-to-end testing.
*   API endpoints secure and responsive, with no unauthorized access.
*   Application passes performance benchmarks (e.g., load times under 2s).
*   Full review of prompts, plans, tasks, and iterations shows adherence to spec-driven process.

## Governance
This Constitution supersedes all other practices and documentation. Amendments require thorough documentation, approval by core stakeholders, and a clear migration plan for affected systems. All Pull Requests and code reviews MUST verify compliance with these principles. Technical complexity MUST be justified by clear business value or critical non-functional requirements.

**Version**: 1.0.0 | **Ratified**: 2026-01-24 | **Last Amended**: 2026-01-24
