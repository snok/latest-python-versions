# Latest Python Versions

Github Action that fetches the latest Python minor versions available.

Enables you to move from statically defined (and maintained) matrices to
dynamic ones.

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

The action produces an `output` that can be accessed using:

```
${{ steps.get-python-versions.outputs.latest-python-versions }}
```

See examples below for recommended usage.

## Examples

### Normal use

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
      - uses: sondrelg/latest-python-versions@v1
        if: steps.cache-versions.outputs.cache-hit != 'true'
        id: get-python-versions
        with:
          min-version: 3.7
          max-version: 3.10  # defaults to latest when unspecified
          include-prereleases: true  # default false

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
      - uses: sondrelg/latest-python-versions@v1
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
      matrix: ${{fromJson(needs.get-python-versions.outputs.python-matrix)}}
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
```
