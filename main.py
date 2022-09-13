from distutils.util import strtobool
import datetime
import json
import subprocess
import sys

import requests
from packaging import version as semver

GHA_PYTHON_VERSIONS_URL = 'https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json'
EOL_PYTHON_VERSIONS_URL = 'https://endoflife.date/api/python.json'

def main(min_version: str, max_version: str, include_prereleases: str) -> None:
    """
    Set a LATEST_PYTHON_VERSIONS environment variable, and a latest-python-versions output,
    containing the latest Python versions found within the specified bounds.

    :param min_version: The major.minor version lower bound or 'EOL'.
    :param max_version: The major.minor version upper bound or 'latest'.
    :param include_prereleases: Whether to include pre-releases. Defaults to false on an action level.
    """
    if min_version.upper() == 'EOL':
        future = datetime.date.today() + datetime.timedelta(3650)
        for release in requests.get(EOL_PYTHON_VERSIONS_URL).json():
            if (
                datetime.date.today() < datetime.date.fromisoformat(release['eol'])
                and datetime.date.fromisoformat(release['eol']) < future
            ):
                future = datetime.date.fromisoformat(release['eol'])
                min_version = semver.parse(release['cycle'])
    else:
        min_version = semver.parse(min_version)
    max_version = semver.parse(max_version) if max_version != 'latest' else semver.parse('4.0')
    parsed_include_prereleases = strtobool(include_prereleases) == 1

    stable_versions = requests.get(GHA_PYTHON_VERSIONS_URL).json()

    versions = {}

    for version_object in stable_versions:
        version = version_object['version']

        if not parsed_include_prereleases:
            if semver.parse(version).is_prerelease:
                continue

        if (major_minor := semver.parse('.'.join(version.split('.')[:2]))) not in versions:
            if min_version <= major_minor <= max_version:
                versions[major_minor] = version

    subprocess.call(['echo', f'"LATEST_PYTHON_VERSIONS={json.dumps(list(versions.values()))}"', '>>', '"$GITHUB_ENV"'])
    subprocess.call(['echo', f'::set-output name=latest-python-versions::{json.dumps(list(versions.values()))}'])
    print(json.dumps(list(versions.values())))


if __name__ == '__main__':
    main(*sys.argv[1:])
