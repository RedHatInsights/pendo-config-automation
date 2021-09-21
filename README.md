# pendo-config-automation

Automated way to publish rules for pages and features to Pendo.

This is the *only* way to add things to Pendo. If you do this manually in the application, they will be deleted by the automation at the next run.

## Adding Items to the config

Typically, pages and features are split into two sections that have one parent. This is so we can identify and group things based on the same selectors.

Note: All beta pages are generated from the same config, just with a `beta` prefix.

An example entry looks like:

```yml
sample application:
  pages:
    All pages:
      url_rules:
        - /foo/bar
        - /foo/bar/**
    Example Page:
      url_rules:
        - /foo/bar/baz
  features:
    _scope: '[data-ouia-bundle="foo"][data-ouia-app-id="bar"]'
    "Example Feature 1":
      selectors:
        - '{} .pf-c-button:contains("Wow!")'
    "Example Feature 2 - Description description":
      selectors:
        - '{}[data-ouia-subnav="baz"] button:contains("Test")'
```

### Pages

Pages follow specific URL rules for page views. You can add as many `url_rules` as you would like. You can also use wildcards in the rules to capture all sub pages if needed.

In the example above, the generated pendo pages will be:

* `_sample application | All Pages`
* `_sample application | Example Page`

Each one of these pages have an associated hash that you can find in `/stash/id_map.yml`.

Example: `'_sample application | All Pages': ZCrgzvF4kg3cldjhQyezsQ9uRZQ`

This will be the page URL in pendo: `https://app.pendo.io/pages/ZCrgzvF4kg3cldjhQyezsQ9uRZQ`

### Features

Features on pages are items like buttons, links, or anything that a user can interact with. These are tracked by button clicks on the item.

#### Scope

The first item `_scope` in the feature section is the common grouping for all the features that follow. This is used so that items across the platform don't trigger counts, even if they have the same text or selector. Many times, we leverage OUIA attribues since they should be on every page on the platform.

In the above example, all the features/selectors should be inside of the `foo` bundle and within the `bar` application.

#### Selectors

Selectors are literal selectors that you would use to target someting in CSS. The underlying logic for it is jquery's Sizzle library. The only difference is that we prefix selectors with `{}` which is shorthand for the `_scope`.

For `Example Feature 1`, the full selector would be:

`[data-ouia-bundle="foo"][data-ouia-app-id="bar"] .pf-c-button:contains("Wow!")`

Spacing of the `{}` is important, because without the trailing space, like in the second exmaple, there is no space after the `data-ouia-app-id`.

If you are testing out selectors and want to double check your work before contributing, you can do

`pendo.Sizzle({selector})` in the web console and you will get an output if your selector is correct.

## Install

### Environment

Setup a virtual environment and install the deps

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Setup secrets

```shell
mkdir ./secrets
cp auth.py.example ./secrets/auth.py
echo '- dummy' > ./secrets/skiplist.yml
touch secrets/__init__.py
```

Fill out the secrets. The pendo cookies are found on app.pendo.io, _not_ on console.redhat.com

## Running

* Make sure to update the auth secrets with your new jwt before each run

```shell
source venv/bin/activate
bash lint.sh
python main.py
python scrub.py # check the results
python scrub.py --dry=false # optionally
```

## Notes

### Skip list

The `skiplist.yml` is a list of groups that will be skipped in the run.
You can add all groups there to skip all... then uncomment one to not skip it.
This does! goof up the stash file though (will make it incomplete).

### Dry Run

The `DRY_RUN` flag in `main.py` determines if the data will actually be added/removed from pendo.

* DRY_RUN=False means it's a real run
* DRY_RUN=True means it's in debug mode

### Stash list

This list is an automatically maintained list of the 'names' we have for each page and the IDs
for that page that are assigned Pendo side. This should be committed after runs to give us hints
about how things are changing over time, and provide a canonical record of objects the automation
maintains over time.

We *could* (but never have) use this to go back and reinstate a deleted or renamed object
that got a new ID. We could look and say the old ID for `_advisor - foo/bar` was $ID try to make a new
object with the same ID in Pendo (again we never have needed to do this).

The stash list is used by our scrubber to ensure that only things that are managed by automation
exists in the managed groups (groups that start with "_").

The stash list is also used by folks ingesting info from Pendo... to diff and figure out what needs to
be re-ingested.

### Scrubber

You really want to do a complete run (no skip) before running the scrubber.
This ensures the stash file is complete so valid things don't get scrubbed.

### Splitting the config.yml

Given more time I was going to split up the config.yml into multiple files.
So that there was one file per group. I would also split up the stash file to match.
This would let you more easily do partial runs (only a single group for instance) and
not nuke the stash file.

