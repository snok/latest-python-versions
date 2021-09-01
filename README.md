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
    max-version: 3.10  # not required - defaults to latest
    include-prereleases: true  # not required - defaults to false
```

The action produces an `output` that can be accessed using:

```
${{ steps.get-python-versions.outputs.latest-python-versions }}
```

See examples below for recommended usage.

## Example

```yaml
name: Test

on: pull_request

jobs:
  linting:
    ...

  # Define the job to run before your matrix job
  get-python-versions:
    runs-on: ubuntu-latest
    outputs:
      python-matrix: ${{ steps.get-python-versions-action.outputs.latest-python-versions }}
    steps:
    - uses: snok/latest-python-versions@v1
      id: get-python-versions-action
      with:
        min-version: 3.8
        include-prereleases: true

  # Then use the output from the previous job in the matrix definition
  test:
    needs: [linting, get-python-versions]
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ${{ fromJson(needs.set-python-versions.outputs.python-matrix) }}
    steps:
      - uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
```

## Contributing

Contributions are always welcome 👏
