#!/bin/bash

python -m uvicorn api.app:app --host 0.0.0.0 --port 7860
