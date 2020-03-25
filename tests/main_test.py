import pytest

from unidown.main import main


def test_run(tmp_path):
    with pytest.raises(SystemExit) as se:
        main(['--root', str(tmp_path), '--plugin', 'test', '--log', 'CRITICAL'])

    assert se.value.code == 0
    assert tmp_path.joinpath('savestates/test_save.json').exists()
    assert tmp_path.joinpath('downloads/test/README.rst').exists()


def test_print_list():
    with pytest.raises(SystemExit) as se:
        main(['--list-plugins'])

    assert se.value.code == 0
