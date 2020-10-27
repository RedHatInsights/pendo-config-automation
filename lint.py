#!/usr/bin/env python

import sys
import yaml
import re

CONFIG = './data/config.yml'
REG_IDS = re.compile('.*-id-[0-9]+.*')
MISSING_SPACE_AFTER_PARAMS = re.compile('.*?[a-z]\[.*?\][a-z].*')

errors = []

def add_error(s):
    errors.append(s)

with open(CONFIG, 'r') as config_yml:
    try:
        yml = yaml.safe_load(config_yml)
    except Exception as e:
        print('Error: Unable to parse yaml config file ({})'.format(CONFIG))
        print('Details: """')
        print(e)
        print('"""')
        sys.exit(1)

    for group_name, group in yml.items():
        if not 'pages'    in group:
            add_error('Error: no *pages* section found in group "{}"'.format(group_name))

        # if not 'features' in group:
        #     print('Error: no *features* section found in group "{}"'.format(group_name))
        #     sys.exit(1)

        if 'features' in group:
            for feature_name, feature in group['features'].items():
                if 'selectors' not in feature:
                    add_error('Error: found a feature without a "selectors" array ({} -> {})'.format(group_name, feature_name))
                for selector in feature['selectors']:
                    if MISSING_SPACE_AFTER_PARAMS.match(selector):
                        add_error('Error: found a selector that has no space after a param block "example: [...]button" ({} -> {} -> {})'.format(group_name, feature_name, selector))
                    if REG_IDS.match(selector):
                        add_error('Error: found an id-NN pattern in a feature selector ({} -> {} -> {})'.format(group_name, feature_name, selector))

        for page_name, page in group['pages'].items():
            if page_name == 'All':
                add_error('Error: found a page name of "All" the standard is "All pages" ({} -> {})'.format(group_name, page_name))
            for url in page['url_rules']:
                if not url.startswith('//cloud.redhat.com'):
                    add_error("""Error: invalid page URL prefix in the group "{}" on the page "{}"
  Found:    {}
  Expected: //cloud.redhat.com/*'""".format(group_name, page_name, url))

if len(errors):
    print('Custom linter found {} error(s)\n'.format(len(errors)))
    for num, error in enumerate(errors, start = 1):
        print('#### {} ####'.format(num))
        print(error)
        print()
    sys.exit(1)
