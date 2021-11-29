#!/bin/bash
set -e

if [ -z "$TRAVIS" ]
then
    source venv/bin/activate
fi

yamllint ./data/
python lint.py
