#!/bin/bash
set -e

uvicorn main:app --host=0.0.0.0 --reload

exec "$@"
