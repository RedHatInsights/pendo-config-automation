#!/usr/bin/env python
import json
import yaml
import client as client
import time
import sys
import click
import logging
import os

DELAY=1

log = logging.getLogger("pendo-config")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

def get_skip_list():
    with open('./secrets/skiplist.yml') as data:
        yml = yaml.safe_load(data)
        return yml

# Send the data to the pendo
def main_loop(path, is_beta, dry_run):
  with open(path, 'r') as data:
    yml = yaml.safe_load(data)
    skip_list = get_skip_list()
    for name, group in yml.items():
        if name in skip_list:
            log.info(f'Skipping group: [{name}]')
            continue

        if is_beta:
            name = f'_beta {name}'

        log.info(f'Creating group: [{name}]')
        if not dry_run:
            pendo_group = client.create_group_idempotent(name, client.get_color(name, group))

        if 'pages' in group:
            for page_name, page in group['pages'].items():
                for i, url in enumerate(page['url_rules']):
                    page['url_rules'][i] = '//*{}'.format(page['url_rules'][i])
                    if is_beta:
                        page['url_rules'][i] = page['url_rules'][i].replace('//*/', '//*/beta/')

                log.info(f'Creating page: [{page_name}] {page}')
                if not dry_run:
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

                log.info(f'Creating feature: [{feature_name}] {feature}')
                if not dry_run:
                    client.create_feature_in_group(pendo_group, feature_name, feature)
                    time.sleep(DELAY)

# Check if app exists in main.yml
def check_app(appName):
  log.info('Checking if app exists in main.yml')
  with open('./data/main.yml', 'r') as data:
    yml = yaml.safe_load(data)
    ymlArray = yml["applications"]
    if appName in ymlArray:
      log.info('App exists')
      return True
    else:
      log.info('App does not exist')
      return False

# Build the app using main_loop
def build_app(appName, dry_run):
  log.info(f'Building: {appName}')
  location = './data/'
  appFile = appName + '.yml'
  fullPathname = location + appFile
  log.info(f'Using file: {appFile}')
  # Stable pages and features
  log.info('Creating stable pages and features')
  main_loop(fullPathname, False, dry_run)
  # Beta pages and features
  log.info('Creating beta pages and features')
  main_loop(fullPathname, True, dry_run)

  if not dry_run: generate_stash(appName)

def generate_stash(appName):
  location = './stash/'
  pathname = appName + '_stash.yml'
  fullPathname = location + pathname
  with open(fullPathname, 'w') as outfile:
      yaml.dump(client.get_ids_map(), outfile)

# main
@click.command()
@click.option(
    '--app',
    '-a',
    type=str,
    default=None,
    help='Name of the app you wish to build',
)
@click.option(
    '--dry-run',
    '-d',
    is_flag=True,
    help='Used to determine if data should actually be added or removed from Pendo',
)
def main(app, dry_run):
  if app:
    log.info(f'App is: {app}')
    if check_app(app):
      build_app(app, dry_run)
  else:
    log.info('No app specified, building all apps')
    with open('./data/main.yml', 'r') as data:
      yml = yaml.safe_load(data)
      ymlArray = yml["applications"]
      for app in ymlArray:
        build_app(app, dry_run)

if __name__ == "__main__":
   main()