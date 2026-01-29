# Research for Todo Resolution Feature

## Decision: API Path Structure - {user_id} in URL vs Internal JWT Filter

**Rationale**: Explicit scoping via {user_id} in URL paths is chosen over internal JWT filtering because:
- It makes the user isolation requirement explicit in the API contract
- It's easier to validate and test that each endpoint properly scopes to the user
- It follows RESTful design principles by making the resource hierarchy clear
- It prevents accidental data leakage if JWT middleware is misconfigured
- It provides better audit trails showing which user accessed what resources

**Alternatives considered**:
- Internal JWT filter: Simpler implementation but less explicit and more prone to security issues
- Query parameter scoping: Less RESTful and potentially logged in server logs

## Decision: JWT Library - python-jose vs PyJWT

**Rationale**: python-jose is chosen over PyJWT because:
- Enhanced robustness and security features
- Better ECDSA support for stronger cryptographic algorithms
- Better alignment with security-first approach in constitution
- Compatibility with Better Auth JWT standards
- More comprehensive security patches and maintenance

**Alternatives considered**:
- PyJWT: Lighter weight but less feature-rich and potentially less secure

## Decision: CORS Origins - Specific Frontend URLs vs Wildcard

**Rationale**: Specific frontend URLs are chosen over wildcard for security:
- Prevents CSRF attacks by restricting which origins can make requests
- Maintains security while allowing local development (localhost:3000) and production access
- Aligns with security-first approach in constitution
- Reduces attack surface compared to wildcard access

**Alternatives considered**:
- Wildcard (*): More flexible for development but significantly less secure
- Environment-based: Would require more complex configuration management

## Decision: Styling Configuration - Full Tailwind Content Paths vs Minimal

**Rationale**: Full Tailwind content paths configuration is chosen:
- Ensures comprehensive rendering of all utility classes
- Addresses styling rendering issues mentioned in spec
- More maintainable in the long term
- Better performance through proper purging of unused classes

**Alternatives considered**:
- Minimal configuration: Quicker fix but may miss styling in some components

## Decision: Database Environment - Neon Serverless vs Local Postgres

**Rationale**: Neon Serverless PostgreSQL is chosen because:
- Auto-scaling capabilities align with scalability requirements
- Cloud persistence ensures data durability
- Serverless nature reduces infrastructure overhead
- Aligns with project constraints in constitution
- Better for multi-user environments

**Alternatives considered**:
- Local Postgres: Better for offline development but lacks cloud benefits and scaling

## Decision: Dependency Management - UV Package Manager

**Rationale**: UV package manager is adopted because:
- Modern reproducibility and speed improvements
- Better lock file handling than pip
- Aligns with maintainability requirements in constitution
- Faster dependency resolution and installation
- Improved virtual environment management

**Alternatives considered**:
- Standard pip/poetry: More familiar but less efficient and reproducible