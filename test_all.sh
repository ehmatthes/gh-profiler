# Run unit tests, and e2e tests.
uv run pytest
uv run pytest tests/e2e_tests -k full
uv run pytest tests/e2e_tests -k concise
