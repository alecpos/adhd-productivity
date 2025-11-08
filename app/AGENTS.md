# Backend implementation guidelines

The `app/` package powers the FastAPI backend. Follow these conventions when working anywhere under
this directory:

- Use type annotations and descriptive docstrings on public functions, classes, and coroutines.
- Prefer asynchronous SQLAlchemy sessions (`AsyncSession`) and async service methods when I/O is
  involved. Keep synchronous helpers pure and side-effect free.
- Reuse shared abstractions:
  - Persistence helpers live in `app/database` and `app/models`.
  - Business logic goes into `app/services` and should inherit from or cooperate with
    `BaseService`/`BaseOptimizerService` where possible.
  - Pydantic request/response models belong in `app/schemas`.
- Handle time zones explicitly using `datetime` objects aware of UTC offsets; never assume naive
  datetimes when touching calendar data.
- Raise custom errors from `app.exceptions` or `app.core.exceptions` instead of bare exceptions so
  the API layer can translate them cleanly.
- Keep integration-specific logic (Google, Outlook, Apple, etc.) inside the dedicated service files
  in `app/services` instead of scattering credentials through other modules.
