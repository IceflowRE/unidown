import pytest
from core.settings import Settings

from unidown.core import manager
from unidown.core.plugin_state import PluginState


def test_init_logging(tmp_path):
    manager.init_logging(Settings(tmp_path, tmp_path.joinpath('UniDown.log')))
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
    assert manager.run(Settings(), name, options) == result
    if PluginState.EndSuccess == result:
        pass
        #assert tmp_path.joinpath('savestates/test_save.json').exists()
