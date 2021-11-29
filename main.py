#!/usr/bin/env python
import json
import yaml
import client as client
import time
import sys
import getopt

DELAY=1
DRY_RUN=True

def get_skip_list():
    with open('./secrets/skiplist.yml') as data:
        yml = yaml.safe_load(data)
        return yml

# Send the data to the pendo
def main_loop(path, is_beta):
  with open(path, 'r') as data:
    yml = yaml.safe_load(data)
    skip_list = get_skip_list()
    for name, group in yml.items():
        if name in skip_list:
            print ('Skipping group: [{}]'.format(name))
            continue

        if is_beta:
            name = '_beta {}'.format(name)

        print('Creating group: [{}]'.format(name))
        if not DRY_RUN:
            pendo_group = client.create_group_idempotent(name, client.get_color(name, group))

        if 'pages' in group:
            for page_name, page in group['pages'].items():
                for i, url in enumerate(page['url_rules']):
                    page['url_rules'][i] = '//*{}'.format(page['url_rules'][i])
                    if is_beta:
                        page['url_rules'][i] = page['url_rules'][i].replace('//*/', '//*/beta/')

                print('- Creating page: [{}] {}'.format(page_name, page))
                if not DRY_RUN:
                    client.create_page_in_group(pendo_group, page_name, page)
                    time.sleep(DELAY)

        if 'features' in group and not is_beta:
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

# Check if app exists in main.yml
def check_app(appName):
  print ('Checking if app exists in main.yml')
  with open('./data/main.yml', 'r') as data:
    yml = yaml.safe_load(data)
    ymlArray = yml["applications"]
    if appName in ymlArray:
      print ('App exists')
      return True
    else:
      print ('App does not exist')
      return False

# Build the app using main_loop
def build_app(appName):
  print ('Building:', appName)
  location = './data/'
  appFile = appName + '.yml'
  fullPathname = location + appFile
  print ('Using file:', appFile)
  # Stable pages and features
  print ('Creating stable pages and features')
  main_loop(fullPathname, False)
  # Beta pages and features
  print ('Creating beta pages and features')
  main_loop(fullPathname, True)

  # if not DRY_RUN: generate_stash(appName)

def generate_stash(appName):
  location = './test/'
  pathname = appName + '_stash.yml'
  fullPathname = location + pathname
  with open(fullPathname, 'w') as outfile:
      yaml.dump(client.get_ids_map(), outfile)

# main
def main(argv):
  appName = ''
  try:
    opts, args = getopt.getopt(argv,"ha:",["app="])
  except getopt.GetoptError:
    print ('test.py -a <app>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
        print ('test.py -a <app>')
        sys.exit()
    elif opt in ("-a", "--app"):
        appName = arg
  
  if appName:
    print ('App is:', appName)
    if check_app(appName):
      build_app(appName)
  else:
    print ('No app specified, building all apps')
    with open('./data/main.yml', 'r') as data:
      yml = yaml.safe_load(data)
      ymlArray = yml["applications"]
      for app in ymlArray:
        print ('Building:', app)
        build_app(app)

# if not DRY_RUN:
#     with open('./stash/id_map.yaml', 'w') as outfile:
#         yaml.dump(client.get_ids_map(), outfile)

if __name__ == "__main__":
   main(sys.argv[1:])