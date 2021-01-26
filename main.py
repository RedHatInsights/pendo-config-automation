#!/usr/bin/env python
import json
import yaml
import client as client
import time

DELAY=1
DRY_RUN=False

def get_skip_list():
    with open('./secrets/skiplist.yml') as data:
        yml = yaml.safe_load(data)
        return yml

with open('./data/config.yml', 'r') as data:
    yml = yaml.safe_load(data)
    skip_list = get_skip_list()
    for name, group in yml.items():

        if name in skip_list:
            print ('Skipping group: [{}]'.format(name))
            continue

        print('Creating group: [{}]'.format(name))
        if not DRY_RUN:
            pendo_group = client.create_group_idempotent(name, client.get_color(name, group))

        if 'pages' in group:
            for page_name, page in group['pages'].items():
                for i, url in enumerate(page['url_rules']):
                    page['url_rules'][i] = '//*.redhat.com{}'.format(page['url_rules'][i])

                print('- Creating page: [{}] {}'.format(page_name, page))
                if not DRY_RUN:
                    client.create_page_in_group(pendo_group, page_name, page)
                    time.sleep(DELAY)

        if 'features' in group:
            scope = False
            if '_scope' in group['features']:
                scope = group['features']['_scope']
                del group['features']['_scope']

            for feature_name, feature in group['features'].items():
                if scope:
                    for i, selector in enumerate(feature['selectors']):
                        txt = feature['selectors'][i]
                        txt = txt.replace('{}', scope, 1)
                        feature['selectors'][i] = txt

                print('- Creating feature: [{}] {}'.format(feature_name, feature))
                if not DRY_RUN:
                    client.create_feature_in_group(pendo_group, feature_name, feature)
                    time.sleep(DELAY)

with open('./stash/id_map.yaml', 'w') as outfile:
    yaml.dump(client.get_ids_map(), outfile)
