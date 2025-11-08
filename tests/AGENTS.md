# Testing guidelines

- Use `pytest` style tests with descriptive function names (e.g., `test_service_handles_missing_token`).
- Prefer async test helpers and `pytest.mark.asyncio` when exercising async services.
- Co-locate fixtures within the relevant subdirectories (see `tests/services/conftest.py` etc.) to
  keep scope targeted.
- When mocking calendar providers, rely on the shared fakes in `tests/services` instead of creating
  ad-hoc mocks.
- Keep assertions focused: one behaviour per test with clear Arrange/Act/Assert sections separated by
  blank lines.
