#!/bin/bash

set -ue

# docker compose down
docker compose -f compose.experiment.yaml down

# setup.py
./.venv/bin/python ./src/experiments/setup/setup.py

# docker compose up 
docker compose -f compose.experiment.yaml up -d
sleep 5.0

# initialize.py
.venv/bin/python ./src/experiments/initialize.py
