#!/usr/bin/env python

import sys
import yaml
import re

CONFIG = './data/config.yml'
REG_IDS = re.compile('.*-id-[0-9]+.*')


with open(CONFIG, 'r') as config_yml:
    try:
        yml = yaml.safe_load(config_yml)
    except Exception as e:
        print('Error: Unable to parse yaml config file ({})'.format(CONFIG))
        print('Details: """')
        print(e)
        print('"""')
        sys.exit(1)

    for name, group in yml.items():
        if not 'pages'    in group:
            print('Error: no *pages* section found in group "{}"'.format(name))
            sys.exit(1)
        if not 'features' in group:
            print('Error: no *features* section found in group "{}"'.format(name))
            sys.exit(1)

        for feature_name, feature in group['features'].items():
            if 'selectors' not in feature:
                print('Error: found a feature without a "selectors" array ({} -> {})'.format(name, feature_name))
                sys.exit(1)
            for selector in feature['selectors']:
                if REG_IDS.match(selector):
                    print('Error: found an id-NN pattern in a feature selector ({} -> {} -> {})'.format(name, feature_name, selector))
                    sys.exit(1)

        for page_name, page in group['pages'].items():
            for url in page['url_rules']:
                if not url.startswith('//cloud.redhat.com'):
                    print('Error: invalid page URL prefix in the group "{}" on the page "{}"'.format(name, page_name))
                    print()
                    print('Found:    {}'.format(url))
                    print('Expected: //cloud.redhat.com/*')
                    sys.exit(1)
