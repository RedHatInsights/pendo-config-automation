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
$ echo '- dummy' > ./secrets/skiplist.yml
$ touch secrets/__init__.py
```

Fill out the secrets. The pendo cookies are found on app.pendio.io, _not_ on cloud.redhat.com

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

