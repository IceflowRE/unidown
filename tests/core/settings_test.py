from unidown.core.settings import Settings


def test_mkdir(tmp_path):
    settings = Settings(tmp_path)
    settings.mkdir()
    assert tmp_path.joinpath('downloads').exists()
    assert tmp_path.joinpath('savestates').exists()
    assert tmp_path.joinpath('temp').exists()
