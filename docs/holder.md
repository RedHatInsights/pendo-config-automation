# Updating the holder file

When a PR is merged, there is a [github action]('./.github/workflows/holder.yml') that adds any `/data/` file to a .yml file.

This allows you to do `python main.py -u` to update all the undeployed files in pendo.

## Setting up secrets

In order to push to the main branch, which is protected, a repo admin has to set up a [personal access token](https://github.com/settings/tokens) with `repo` and `workflow`. Once that is created, add it to the [secrets](https://github.com/RedHatInsights/pendo-config-automation/settings/secrets/actions) in this repository and update the [holder.yml]('./.github/workflows/holder.yml') file with the new values.
