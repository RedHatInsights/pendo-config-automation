#!/bin/bash
set -e

if [ -z "$TRAVIS" ]
then
    source venv/bin/activate
fi

python lint.py
