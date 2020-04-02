import json
import logging

import pytest

from unidown.core import manager
from unidown.core.plugin_state import PluginState
from unidown.core.settings import Settings


def test_get_options_dict(caplog):
    options = manager.get_options([["username=Nasua", "Nasua"], ["wrongArg="], ["=wrongArg2"]])
    result = [
        "'wrongArg=' is not valid and will be ignored.",
        "'=wrongArg2' is not valid and will be ignored.",
    ]
    assert len(caplog.records) == len(result)
    for actual, expect in zip(caplog.records, result):
        assert actual.msg == expect
    assert options == {'username': "Nasua Nasua"}


test_options = [
    ('not_existing_plugin', [[]], PluginState.NotFound),
    ('test', [["behaviour=load_crash"]], PluginState.LoadCrash),
    ('test', [["behaviour=run_fail"]], PluginState.RunFail),
    ('test', [["behaviour=run_crash"]], PluginState.RunCrash),
    ('test', [["behaviour=normal"], ["username=Nasua", "Nasua"]], PluginState.EndSuccess),
]


@pytest.mark.parametrize('name,options,result', test_options)
def test_run(tmp_path, name, options, result):
    assert manager.run(Settings(tmp_path), name, options) == result
    if PluginState.EndSuccess == result:
        savestate_file = tmp_path.joinpath('savestates/test_save.json')
        assert savestate_file.exists()
        with savestate_file.open(encoding="utf8") as reader:
            actual = json.loads(reader.read())
        assert actual == {
            'meta': {'version': '1'},
            'pluginInfo': {'name': 'test', 'version': '0.1.0', 'host': 'raw.githubusercontent.com'},
            'lastUpdate': '19990909T090909.000000Z',
            'linkItems': {
                '/IceflowRE/unidown/master/README.rst': {'name': 'README_d.rst', 'time': '20010101T010101.000000Z'},
                '/IceflowRE/unidown/master/LICENSE.md': {'name': 'README.rst', 'time': '20010101T010101.000000Z'}
            },
            'username': 'Nasua Nasua'
        }
