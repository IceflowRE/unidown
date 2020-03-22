import pytest

from unidown import dynamic_data


def test_check_dirs(tmp_path):
    dynamic_data.init_dirs(tmp_path)
    with dynamic_data.TEMP_DIR.open('wb') as writer:
        writer.write(str.encode('test'))
    with pytest.raises(FileExistsError):
        dynamic_data.check_dirs()
