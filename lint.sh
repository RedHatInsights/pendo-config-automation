#!/bin/bash
set -e

if [ -z "$TRAVIS" ]
then
    source venv/bin/activate
fi

yamllint ./data/config.yml
python lint.py
