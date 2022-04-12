#!/bin/bash
set -e

yamllint ./data/
python lint.py
