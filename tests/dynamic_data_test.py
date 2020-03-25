import pytest

from core.settings import Settings


def test_check_dirs(tmp_path):
    settings = Settings(tmp_path)
    with settings.temp_dir.open('wb') as writer:
        writer.write(str.encode('test'))
    with pytest.raises(FileExistsError):
        settings.check_dirs()
