# Latest Python Versions

Fetches the latest Python minor version available in Github Actions.

Python version matrices constantly need to be updated.
This is a bit of a nuisance, but important - especially if you're trying to keep
your software compatible with the latest Python versions.

In short, this action lets you move from a statically defined version matrix,
to a dynamic one.

Versions are fetched from [here](https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json).

## Usage

To use the action, simply throw this into one of your workflows

```yaml
- uses: sondrelg/latest-python-versions@v1
  id: get-python-versions
  with:
    min-version: 3.7
    max-version: 3.10
    include-prereleases: true
```

This will produce an `output` that can be accessed with `${{ steps.get-python-versions.outputs.latest-python-versions }}`.

The output must always be referenced as `latest-python-versions`, while the second element in the output must just match
the `id` of the step you defined for the action run.

See examples for recommended use.

### Example

## Normal use

```yaml
name: Test

on: pull_request

jobs:
  set-python-versions:
    runs-on: ubuntu-latest
    outputs:
      python-matrix: ${{ steps.get-python-versions.outputs.latest-python-versions }}
    steps:
      - uses: actions/checkout@v2
      - uses: sondrelg/latest-python-versions@v1
        if: steps.cache-versions.outputs.cache-hit != 'true'
        id: get-python-versions
        with:
          min-version: 3.7
          max-version: 3.10  # defaults to latest when unspecified
          include-prereleases: true  # default false

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

If you wanted to save Github some traffic, you
should be able to cache the action results pretty simply.

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
      - name: Set cache key based on week number, so cache expires once a week
        id: set-cache-key
        run: |
          week_number=$(date +%V)
          echo "::set-output name=cache-key::$week_number"
      - name: Load cached versions
        uses: actions/cache@v2
        id: cache-versions
        with:
          path: .python-versions-file
          key: ${{ steps.set-cache-key.outputs.cache-key }}
      - uses: sondrelg/latest-python-versions@v1
        if: steps.cache-versions.outputs.cache-hit != 'true'
        id: get-python-versions
        with:
          min-version: 3.7
          max-version: 3.10
          include-prereleases: true
      - name: Create new .python-versions-file
        run: echo "${{ steps.get-python-versions.outputs.latest-python-versions }}" > .python-versions-file
        if: steps.cache-versions.outputs.cache-hit != 'true'
      - name: Export .python-versions-file
        id: export-python-versions
        run: |
          versions=$(cat .python-versions-file)
          echo "::set-output name=python-versions::$versions"
  test:
    needs: get-python-versions
    runs-on: ubuntu-latest
    strategy:
      matrix: ${{fromJson(needs.get-python-versions.outputs.python-matrix)}}
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
```
