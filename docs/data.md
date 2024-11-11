# Adding Data

Each application should have their own file inside of `/data/APP.yml`. Whenever changing your selectors or pages, make sure you are updating the correct file.

## Adding a new app

If you are adding a new app, add all of your pages and features (described below) to the `data/` folder with the correct name and then add it to the master list in `data/main.yml`

## Pages and Features

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

Each one of these pages have an associated hash that you can find in `/stash/APP.yml`.

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

Spacing of the `{}` is important, because without the trailing space, like in the second example, there is no space after the `data-ouia-app-id`.

If you are testing out selectors and want to double check your work before contributing, you can do

`pendo.Sizzle('selector')` in the web console and you will get an output if your selector is correct.

Ex: `pendo.Sizzle('[data-ouia-bundle="foo"][data-ouia-app-id="bar"] .pf-c-button:contains("Wow!")')`
