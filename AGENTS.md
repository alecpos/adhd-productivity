# Repository-wide guidelines

Welcome to the ADHD Productivity platform. Please observe these conventions for any work that
spans the repository:

- Prefer incremental, well-scoped commits with descriptive messages (no force-pushes to shared
  branches).
- Match existing tooling: Python code is formatted with Black (line length 100) and linted with
  Ruff (line length 88); JavaScript/TypeScript code is handled by Next.js/ESLint defaults.
- When you touch multiple stacks (Python backend + Next.js frontend), keep behavioural changes
  isolated per commit whenever possible.
- Keep documentation and diagrams in Markdown unless the scope explicitly requires another format.
- Coordinate calendar integrations through the dedicated services in `app/services` and the Next.js
  frontend—avoid duplicating OAuth client logic outside those locations.
