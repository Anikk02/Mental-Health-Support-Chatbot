#!/usr/bin/env bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# create indexes
python -c "from backend.app.indexes_setup import create_indexes; import asyncio; asyncio.run(create_indexes())"
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
