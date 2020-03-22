import pytest

from unidown import dynamic_data
from unidown.main import main


def test_run(tmp_path):
    dynamic_data.DISABLE_TQDM = True
    with pytest.raises(SystemExit) as se:
        main(['--main', str(tmp_path), '--plugin', 'test', '--log', 'CRITICAL'])

    assert se.value.code == 0
    assert tmp_path.joinpath('savestates/test_save.json').exists()
    assert tmp_path.joinpath('downloads/test/README.rst').exists()


def test_run_perm_error(tmp_path):
    tmp_path.chmod(0o0100)
    dynamic_data.DISABLE_TQDM = True
    with pytest.raises(SystemExit) as se:
        main(['--main', str(tmp_path), '--plugin', 'test', '--log', 'CRITICAL'])

    assert se.value.code == 1


def test_print_list():
    with pytest.raises(SystemExit) as se:
        main(['--list-plugins'])

    assert se.value.code == 0
