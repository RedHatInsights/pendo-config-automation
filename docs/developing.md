# Developing

## Setup

### Environment

Setup a virtual environment and install the deps

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Secrets

```shell
mkdir ./secrets
cp auth.py.example ./secrets/auth.py
touch secrets/__init__.py
```

Fill out the secrets. The pendo cookies are found on app.pendo.io, _not_ on console.redhat.com

## Running

* Make sure to update the auth secrets with your new jwt before each run

### Updating data in Pendo

The main.py file uploads the data from `data/*.yml` to pendo.

#### Running the debug mode

This is useful for checking the output before doing a real run

```shell
source venv/bin/activate
bash lint.sh
python main.py --dry-run
```

#### Running the entire suite

```shell
source venv/bin/activate
bash lint.sh
python main.py
```

#### Running an application

```shell
source venv/bin/activate
bash lint.sh
python main.py -a {APP}
```

#### Running a select group of applications

```shell
source venv/bin/activate
bash lint.sh
python main.py -a {APP1} -a {APP2} ... 
```

#### Running all undeployed files from holder.yml

```shell
source venv/bin/activate
bash lint.sh
python main.py -u 
```

#### Clear holder.yml

```shell
source venv/bin/activate
bash lint.sh
python main.py -c
```

### Scrubbing existing data

Note: **This should be done after the upload is done**

In order to maintain a fresh list used in this config, there is a scrubber that will remove files that looks like it was added by this automation, but was not. We want to scrub that in order to keep our stash list fresh.

#### Scrubbing in debug mode

```shell
source venv/bin/activate
python scrub.py --dry-run
```

#### Scrubbing real data

```shell
source venv/bin/activate
python scrub.py
```
