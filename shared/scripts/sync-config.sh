#!/bin/bash
# Configuration sync script for easier access

cd "$(dirname "$0")"/../backend
python -m app.cli config "$@"