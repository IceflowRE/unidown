from pathlib import Path

import pytest

from unidown import dynamic_data
from unidown.core import manager
from unidown.core.plugin_state import PluginState


def test_init(tmp_path):
    manager.init(tmp_path, Path('UniDown.log'), dynamic_data.LOG_LEVEL)
    assert tmp_path.joinpath('downloads').exists()
    assert tmp_path.joinpath('savestates').exists()
    assert tmp_path.joinpath('temp').exists()
    assert tmp_path.joinpath('UniDown.log').is_file()


test_options = [
    ('not_existing_plugin', [], PluginState.NotFound),
    ('test', ["behaviour=load_crash"], PluginState.LoadCrash),
    ('test', ["behaviour=run_fail"], PluginState.RunFail),
    ('test', ["behaviour=run_crash"], PluginState.RunCrash),
    ('test', ["behaviour=normal"], PluginState.EndSuccess),
]


@pytest.mark.parametrize('name,options,result', test_options)
def test_run(name, options, result):
    assert manager.run(name, options) == result
