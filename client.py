import sys
import json
import requests
import random
import secrets.auth as auth

PREFIX = '_'

HEADERS = {
    'content-type': 'application/json',
    'x-pendo-xsrf-token': auth.get_xsrf(),
    'cookie': '; '.join(auth.get_cookies()),
}

ids_map = {}
s = requests.Session()
s.headers.update(HEADERS)

class CacheGetter:
    cache = {}

    def get(self, input_url):
        r = s.get(url(input_url))
        r.raise_for_status()
        json_data = r.json()

        if not input_url in self.cache:
            log('cache miss for: {}'.format(input_url))
            self.cache[input_url] = json_data
            return json_data

        log('cache hit for: {}'.format(input_url))
        return self.cache[input_url]

cache_getter = CacheGetter()

def log(msg):
    print('> DEBUG: {}'.format(msg), file=sys.stderr)

def stash_ids(pendo_id, config_id):
    ids_map[config_id] = pendo_id

def get_ids_map():
    return ids_map

def get_name(name):
    if name.startswith(PREFIX):
        return name
    return PREFIX + name

def get_feature_full_name(group_name, feature_name):
    return '{} | {}'.format(group_name, feature_name)

def url(path):
    return 'https://app.pendo.io/api/s/5300167311360000{}'.format(path)

def _create_feature_idempotent(name, data):
    log('looking for feature: {}'.format(name))
    for feature in cache_getter.get('/feature?expand=*'):
        if feature['name'] == name:
            log('found feature [{}] {}'.format(feature['id'], name))
            stash_ids(feature['id'], name)
            return feature
    return _create_feature(name, data)

def _create_feature(name, data):
    payload = {
        "appId": 6245718179446784,
        "kind": "Feature",
        "name": name,
        "color": "",
        "eventPropertyConfigurations": [],
        "elementPathRules": data['selectors']
    }

    if 'page_id' in data:
        log('setting page_id {}'.format(data['page_id']))
        payload['pageId'] = data['page_id']

    r = s.post(url('/feature?includeMobileRuleset=1'), json = payload)

    r.raise_for_status()
    feature = r.json()

    log('created feature [{}] {}'.format(feature['id'], feature['name']))
    stash_ids(feature['id'], feature['name'])
    return feature

def _create_page(page_full_name, page_data):
    # POST https://app.pendo.io/api/s/5300167311360000/page?includeMobileRuleset=1
    # {"name":"Test123","rules":[{"rule":"//*/insights","designerHint":"https://cloud.redhat.com/insights/"}],"appId":6245718179446784}
    r = s.post(url('/page?includeMobileRuleset=1'), json = {
        "appId": 6245718179446784,
        "name": page_full_name,
        "rules": list(map(lambda u : { "rule": u }, page_data['url_rules']))
    })

    r.raise_for_status()
    page = r.json()
    log('created page [{}] {}'.format(page['id'], page_full_name))
    stash_ids(page['id'], page_full_name)
    return page

def _create_page_idempotent(page_full_name, page_data):
    log('looking for page: {}'.format(page_full_name))

    for page in cache_getter.get('/page?expand=*'):
        if page['name'] == page_full_name:
            log('found page [{}] {}'.format(page['id'], page_full_name))
            stash_ids(page['id'], page_full_name)
            return page

    return _create_page(page_full_name, page_data)

def create_page_in_group(group, page_name, page_data):
    page_full_name = get_feature_full_name(group['name'], page_name)
    page = _create_page_idempotent(page_full_name, page_data)

    # POST https://app.pendo.io/api/s/5300167311360000/page/H9FF-czQ7RZTTb9aUB4fBbk3Cdo/apply
    # no data?
    r = s.post(url('/page/{}/apply'.format(page['id'])))
    r.raise_for_status()

    # PUT https://app.pendo.io/api/s/5300167311360000/group/G7YaDIq_AjRz-1Y6m2x2FP_Bbe0/page/H9FF-czQ7RZTTb9aUB4fBbk3Cdo
    # no data?
    r = s.put(url('/group/{}/page/{}'.format(group['id'], page['id'])))
    r.raise_for_status()

    _ensure_page_url_rules(page_full_name, page['id'], page_data['url_rules'], page['rules'])

def _ensure_page_url_rules(page_name, page_id, input_rules, existing_rules):
    input_rules = list(map(lambda u : { "rule": u }, input_rules))
    existing_rules = list(map(lambda u : { "rule": u['rule'] }, existing_rules))
    if not input_rules == existing_rules:
        r = s.put(url('/page/{}'.format(page_id)), json = {
            "name": page_name,
            "rules": input_rules
        })
        r.raise_for_status()
        log('added rules to page [{}] {}'.format(page_id, input_rules))
        stash_ids(page_id, input_rules)

def create_feature_in_group(group, feature_name, feature_data):
    feature_full_name = get_feature_full_name(group['name'], feature_name)
    feature = _create_feature_idempotent(feature_full_name, feature_data)
    _set_feature_app_name(feature['id'])
    _add_feature_to_group(group['id'], feature['id'])
    _ensure_feature_rules(feature_full_name, feature['id'], feature_data['selectors'], feature['elementPathRules'])

def _ensure_feature_rules(feature_name, feature_id, input_selectors, existing_selectors):
    #  PUT https://app.pendo.io/api/s/5300167311360000/feature/HPfHlgH8MgHemhfc_YTeLrV_RNE
    if not input_selectors == existing_selectors:
        r = s.put(url('/feature/{}'.format(feature_id)), json = {
            "name": feature_name,
            "elementPathRules": input_selectors
        })
        r.raise_for_status()
        log('added selectors to feature [{}] {}'.format(feature_id, input_selectors))
        stash_ids(feature_id, input_selectors)

def _set_feature_app_name(feature_id):
    r = s.post(url('/feature/{}/apply'.format(feature_id)), json = {
        "namespace": "Red_Hat_Customer_Portal",
        "type": "PageFeatures",
        "applicationName": "cloud_redhat_com"
    })

    r.raise_for_status()
    log('set app name on feature [{}]'.format(feature_id))

def _add_feature_to_group(group_id, feature_id):
    r = s.put(url('/group/{}/feature/{}'.format(group_id, feature_id)), json = {
        "itemId": feature_id,
        "itemType": "Feature"
    })

    r.raise_for_status()
    log('added feature [{}] to group [{}]'.format(feature_id, group_id))
    # stash_ids(feature_id, group_id)

def _int_to_color_str(i):
    return '.groupColor{:02d}'.format(i)

def get_color(name, group):
    if 'color' in group:
        color = int(group['color'])
        assert color > 0 and color <= 10, "Color for group `{}` is not an int between 1 and 10".format(name)
        if color > 0 and color <= 10:
            color_str = _int_to_color_str(color)
            log('setting group color: {}'.format(color_str))
            return color_str

    color_str = _int_to_color_str(random.randint(1,10))
    log('setting random group color: {}'.format(color_str))
    return color_str

def create_group_idempotent(name, color):
    name = get_name(name)
    for group in cache_getter.get('/group'):
        if group['name'] == name:
            log('found group {}'.format(group['id']))
            stash_ids(group['id'], group['name'])
            return group

    group = _create_group(name, color)
    log('created group {}'.format(group['id']))
    stash_ids(group['id'], group['name'])
    return group

def _create_group(name, color):
    name = get_name(name)
    r = s.post(url('/group'), json = {
        'name': name,
        'description': '',
        'color': color,
        'items': [],
    })
    r.raise_for_status()
    return r.json()
