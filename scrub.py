#!/usr/bin/env python

import sys
import json
import client as client

DRY_RUN = False

def _del(t, eid):
    if not DRY_RUN:
        client.delete_entity(t, eid)

def delete_entities(t):
    r = client.get_entity(t)
    for feature in r:
        if feature['appId'] == 6245718179446784:
            eid = feature['id']
            group_name = feature['group']['name']
            name = feature['name']
            created_by = feature['createdByUser']['username']
            last_updated_by = feature['lastUpdatedByUser']['username']
            kind = feature['kind']
            if group_name.startswith('_'):
                if created_by not in ['ihands@redhat.com', 'rlong@redhat.com'] or last_updated_by not in ['ihands@redhat.com', 'rlong@redhat.com'] or not name.startswith('_'):
                    print('Removing ({}) {} [{}] created by:{}, last updated by:{}'.format(kind, eid, name, created_by, last_updated_by))
                    _del(t, eid)

if len(sys.argv) > 1:
    if sys.argv[1] == '--dry-run':
        DRY_RUN=True

if not DRY_RUN:
    print('Scrubbing live data, if you want to debug, add --dry-run')

delete_entities('feature')
delete_entities('page')
