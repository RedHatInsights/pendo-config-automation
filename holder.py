#!/usr/bin/env python

import sys
import yaml

FILES_CHANGED = sys.argv[1:]
DATA_DIR = 'data/'
EXTENSION = '.yml'
UNMERGED_FILE = './holder.yml'

UPDATED_APPS = []
PREVIOUS_APPS = []
COMBINED_APPS = []

# Load the apps from previous commit (passed from .sh file)
filtered_array = [file for file in FILES_CHANGED if file.startswith(DATA_DIR)]

# Remove the file prefix and the extension
for file in filtered_array:
  FILE_NAME = file.replace(DATA_DIR, '')
  APP = FILE_NAME.replace(EXTENSION, '')
  UPDATED_APPS.append(APP)

# Get current list of unmerged apps
with open(UNMERGED_FILE, 'r') as data:
  yml = yaml.safe_load(data)
  if yml:
    COMBINED_APPS = yml + UPDATED_APPS
  else:
    COMBINED_APPS = UPDATED_APPS

# Remove duplicates
DEDUPED_APPS = list(set(COMBINED_APPS))

# Push new list to yml file
print('Adding: ', DEDUPED_APPS)
with open(UNMERGED_FILE, 'w') as outfile:
    yaml.dump(DEDUPED_APPS, outfile)