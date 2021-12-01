#!/bin/bash
set -e

FILES_CHANGED=$(git diff --name-only HEAD HEAD~1)

python addUnmerged.py $FILES_CHANGED