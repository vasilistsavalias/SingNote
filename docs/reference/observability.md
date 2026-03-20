# Observability

There is no dedicated observability stack in this repository today.

## Current State

- no metrics backend
- no tracing integration
- no structured log pipeline
- no dashboards or alert definitions checked into the repo

## Practical Reality

Debugging currently relies on:

- Streamlit runtime output
- Python exceptions and tracebacks
- pytest coverage of core flows

If observability is added later, this page should be expanded and linked to the
real implementation source.
