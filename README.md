# pendo-config-automation

## Install

### Environment

Setup a virtual environment and install the deps
```shell
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### Setup secrets
```shell
$ mkdir ./secrets
$ cp auth.py.example ./secrets/auth.py
$ dummy > ./secrets/skiplist.yml
```

Fill out the secrets.

## Running
```shell
$ source venv/bin/activate
$ bash lint.sh
$ python main.py
$ python scrub.py # check the results
$ python --dry=false scrub.py # optionally
```

## Notes
### Skip list
The `skiplist.yml` is a list of groups that will be skipped in the run.
You can add all groups there to skip all... then uncomment one to not skip it.
This does! goof up the stash file though (will make it incomplete).

### Scrubber
You really want to do a complete run (no skip) before running the scrubber.
This ensures the stash file is complete so valid things don't get scrubbed.

### Splitting the config.yml
Given more time I was going to split up the config.yml into multiple files.
So that there was one file per group. I would also split up the stash file to match.
This would let you more easily do partial runs (only a single group for instance) and
not nuke the stash file.

