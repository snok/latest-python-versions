import json

import pytest
import responses

from main import GHA_PYTHON_VERSIONS_URL, EOL_PYTHON_VERSIONS_URL, main

data = [
    [('3.4', '3.9', 'false'), ['3.9.6', '3.8.11', '3.7.11', '3.6.14', '3.5.10', '3.4.10']],
    [('3.5', '3.9', 'false'), ['3.9.6', '3.8.11', '3.7.11', '3.6.14', '3.5.10']],
    [('3.5', '3.8', 'false'), ['3.8.11', '3.7.11', '3.6.14', '3.5.10']],
    [('3.5', '3.8', 'true'), ['3.8.11', '3.7.11', '3.6.14', '3.5.10']],
    [('3.5', 'latest', 'true'), ['3.10.0-rc.1', '3.9.6', '3.8.11', '3.7.11', '3.6.14', '3.5.10']],
    [('EOL', 'latest', 'true'), ['3.10.0-rc.1', '3.9.6', '3.8.11', '3.7.11']],
]

@responses.activate
@pytest.mark.parametrize('args, result', data)
def test_main_without_max_version(capsys, args, result):
    with open('versions.json') as f:
        responses.add(responses.Response(method='GET', url=GHA_PYTHON_VERSIONS_URL, json=json.load(f)))
    with open('eol.json') as f:
        responses.add(responses.Response(method='GET', url=EOL_PYTHON_VERSIONS_URL, json=json.load(f)))
    main(*args)
    captured = capsys.readouterr()
    print(captured)
    assert json.loads(captured.out) == result
