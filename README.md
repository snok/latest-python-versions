[![release](https://img.shields.io/github/release/snok/latest-python-versions.svg)](https://github.com/snok/latest-python-versions/releases/latest)
[![tests](https://github.com/snok/latest-python-versions/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/snok/latest-python-versions/actions/workflows/test.yml)

# Latest Python Versions

This action will fetch up-to-date data on the latest
Python versions available on Github Actions.

If you're already running tests on multiple Python versions,
this action will allow you to replace your static
matrix definitions with **dynamic** ones.
With a dynamic version matrix definition, you will for example always be
on the latest pre-release of the next upcoming Python release.

The Python versions are fetched from [here](https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json) - the official Github action version manifest.

## Usage

To use the action, simply throw this into one of your workflows

```yaml
- uses: snok/latest-python-versions@v1
  id: get-python-versions
  with:
    min-version: 3.7
    max-version: 3.10  # defaults to latest
    include-prereleases: true  # defaults to false
```

The action produces an `output` that can be accessed using:

```
${{ steps.get-python-versions.outputs.latest-python-versions }}
```

See examples below for recommended usage.

## Examples

### Basic usage

```yaml
name: Test

on: pull_request

jobs:
  # Define this job to run before your other jobs
  set-python-versions:
    runs-on: ubuntu-latest
    outputs:
      python-matrix: ${{ steps.get-python-versions.outputs.latest-python-versions }}
    steps:
      - uses: actions/checkout@v2
      - uses: snok/latest-python-versions@v1
        if: steps.cache-versions.outputs.cache-hit != 'true'
        id: get-python-versions
        with:
          min-version: 3.7
          max-version: 3.10
          include-prereleases: true

  # Then use the output from the previous job in the matrix definition
  test:
    needs: set-python-versions
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ${{fromJson(needs.set-python-versions.outputs.python-matrix)}}
    steps:
      - uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
```

### Caching versions

If you want to save Github some traffic, you
can cache the action results pretty simply.

This example caches versions for one week at the time:

```yaml
name: Test

on: pull_request

jobs:
  get-python-versions:
    runs-on: ubuntu-latest
    outputs:
      python-matrix: ${{ steps.export-python-versions.outputs.python-versions }}
    steps:
      # Set cache key based on week number, so cache expires once a week
      - id: set-cache-key
        run: |
          week_number=$(date +%V)
          echo "::set-output name=cache-key::$week_number"

      # Try to load cached versions by week number
      - name: Load cached versions
        uses: actions/cache@v2
        id: cache-versions
        with:
          path: .python-versions-file
          key: ${{ steps.set-cache-key.outputs.cache-key }}

      # Fetch new versions if no cache was found
      - uses: snok/latest-python-versions@v1
        if: steps.cache-versions.outputs.cache-hit != 'true'
        id: get-python-versions
        with:
          min-version: 3.7
          max-version: 3.10
          include-prereleases: true

      # Save results to file if no cache was found
      - name: Create new .python-versions-file
        run: echo "${{ steps.get-python-versions.outputs.latest-python-versions }}" > .python-versions-file
        if: steps.cache-versions.outputs.cache-hit != 'true'

      # Load file contents and export values
      - name: Export .python-versions-file
        id: export-python-versions
        run: |
          versions=$(cat .python-versions-file)
          echo "::set-output name=python-versions::$versions"
  test:
    needs: get-python-versions
    runs-on: ubuntu-latest
    strategy:
      python-version: ${{fromJson(needs.get-python-versions.outputs.python-matrix)}}
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
```

This example can be modified to more or less any scenario you would want,
and with [composite actions](https://docs.github.com/en/github-ae@latest/actions/creating-actions/creating-a-composite-action)
now being able to call other actions, you can put all your logic into
a composite action to remove the clutter from your workflow definitions.
Take a look [here](utility_workflows/action.yml) if you need inspiration.

If you want to cache _exactly_ the way shown above,
and you don't need to pin patch versions of the primary action,
you can use the composite action we created for this repo. Simply
define your workflows like this:

```yaml
name: Test

on: pull_request

jobs:
  get-python-versions:
    runs-on: ubuntu-latest
    outputs:
      python-matrix: ${{ steps.export-python-versions.outputs.python-versions }}
    steps:
      - uses: snok/latest-python-versions/caching
        with:
          min-version: 3.7
  test:
    needs: get-python-versions
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ${{fromJson(needs.get-python-versions.outputs.python-matrix)}}
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
```

## Contributing

Contributions are always welcome 👏
