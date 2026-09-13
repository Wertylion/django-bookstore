# AI Prompts

These prompts were used to review and improve the Book Store project.

## Code Review Prompt

```text
Review these Django views for correctness, security and testability:
BookListView, NewOrderView, CreateCheckoutSessionView.
Focus on query parameter validation, transactions, user ownership checks,
external service boundaries and missing tests. Return concrete recommendations
and explain which ones are safe to apply.
```

## Test Generation Prompt

```text
Generate pytest-django tests for a Django book store project.
Cover 2-3 models, ModelForms, session cart behavior, checkout flow,
Stripe Checkout integration with mocks, email sending with locmem backend,
language switching and async JSON views. Use factory-boy factories.
Every test must contain the comment:
Generated with AI, reviewed and modified.
```

## Documentation Prompt

```text
Generate concise docstrings for all Django views in shop/views.py,
order/views.py, user_management/views.py and config/views.py.
The docstrings should explain what each view does without restating the code.
```

## README Prompt

```text
Update README.md for a Django Book Store project.
Include setup, migrations, running the server, Docker, pytest, coverage,
internationalization, Stripe test keys and a section called AI Usage that lists
how AI was used in code review, tests and documentation.
```
