# Performance

This repository has lightweight runtime requirements and no explicit
performance subsystem.

## Current Characteristics

- one-process Streamlit app
- local SQLite persistence
- small seed-song dataset
- no background jobs

## Real Performance Levers

- keep seed files compact and valid
- avoid expensive rerender patterns in the Streamlit UI
- keep SQLite access simple and synchronous

## What Does Not Exist Yet

- no benchmark suite
- no profiling docs in the repo
- no synthetic load testing setup
