# Security Model

This project uses a local namespace-based identity model.

## Identity

- No OAuth, JWT, Auth0, or hosted identity provider is required.
- Every request is scoped by namespace.
- Namespace source:
  - REST: `X-Memory-Namespace` header
  - MCP: `namespace` argument or `X-Memory-Namespace` header

## Isolation Rules

- Namespace is normalized server-side.
- All memory reads/writes/deletes are filtered by resolved namespace user.
- Client-provided identifiers are never trusted without namespace checks.

## Input and Error Handling

- Invalid namespace format returns `400`.
- API errors are sanitized; raw stack traces are not returned.
- Sensitive values must not be logged.

## Operational Security

- Keep PostgreSQL credentials in environment variables.
- Restrict network access to `5432` when deploying outside local machine.
- Treat LM Studio/OpenAI-compatible endpoint as an internal dependency; avoid exposing it publicly.
