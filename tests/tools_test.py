from unidown.tools import unlink_dir_rec


class TestDeleteDirRec:
    def test_non_existence(self, tmp_path):
        no_folder = tmp_path.joinpath("./donotexist/")
        assert not no_folder.exists()
        unlink_dir_rec(no_folder)
        assert not no_folder.exists()

    def test_recursive(self, tmp_path):
        for number in range(1, 4):
            with tmp_path.joinpath(str(number)).open('w'):
                pass

        sub_folder = tmp_path.joinpath("sub")
        sub_folder.mkdir(parents=True, exist_ok=True)
        for number in range(1, 4):
            with sub_folder.joinpath(str(number)).open('w'):
                pass
        tmp_path.joinpath("sub2").mkdir()
        unlink_dir_rec(tmp_path)
        assert not tmp_path.exists()
