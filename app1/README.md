# ADHD Productivity App 1 Architecture

This directory hosts a ground-up rebuild of the ADHD productivity backend that is designed
explicitly for Vercel hosting with Supabase providing persistence. It reuses the extensive
Pydantic models from the original codebase while reorganising the application layers into a
cleaner and more deployment-friendly structure.

## Key Goals

- **Serverless Ready** – The ASGI application can be imported directly by Vercel using
  `app1.vercel:app`.
- **Supabase Native** – Persistence is handled through the official Supabase Python client
  with repositories that map the existing schemas to Supabase tables.
- **Schema Reuse** – Existing Pydantic schemas are leveraged to ensure data validation
  remains consistent with the previous implementation.
- **Modular** – Clear boundaries across `core`, `infrastructure`, `domain`, `services`, and
  `api` layers allow future features (e.g., ML powered insights) to plug in cleanly.

## Layout

```text
app1/
  api/               # FastAPI routers and dependencies
  core/              # Configuration, logging, and exception helpers
  domain/            # Data access repositories bound to Supabase
  infrastructure/    # Third-party integration helpers (Supabase client factory)
  services/          # High-level application use cases
  main.py            # Application factory and FastAPI instance
  vercel.py          # Entry point for Vercel deployments
```

## Environment Variables

The new stack expects the following Supabase and Vercel variables to be configured:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` (preferred for server operations) or `SUPABASE_ANON_KEY`
- `SUPABASE_USERS_TABLE` (optional override, defaults to `users`)
- `SUPABASE_TASKS_TABLE` (optional override, defaults to `tasks`)
- `VERCEL_PROJECT` (optional metadata)
- `VERCEL_REGION` (optional metadata)

Configure these variables in your local `.env` file for development and in Vercel's project
settings for production deployments.

## Running Locally

```bash
uvicorn app1.main:app --reload
```

This will launch the FastAPI application under the `/api` prefix as defined in
`Settings.api_prefix`.

## Deployment

Create a `vercel.json` file at the repository root or project configuration pointing to the
`app1/vercel.py` module. Vercel will automatically detect the `app` symbol exported from that
module and serve the FastAPI application.
