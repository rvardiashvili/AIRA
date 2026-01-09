#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.
python -m src.main
