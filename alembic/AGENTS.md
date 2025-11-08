# Alembic migration guidelines

- Generate migrations with Alembic autogenerate tooling when possible; review and hand-edit to ensure
  deterministic ordering and idempotency.
- Use UTC timestamps in revision IDs/descriptions and update the `down_revision` pointer correctly.
- Avoid data migrations inside schema revisions—place data backfills in `scripts/` unless tightly
  coupled to the schema change.
- Keep `env.py` configuration untouched unless you coordinate the change with the backend team.
