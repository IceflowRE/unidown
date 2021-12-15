import pytest

from unidown import meta
from unidown.core import updater


@pytest.mark.parametrize('version,result', [('1.0.0', True), ('100000000.0.0', False)])
def test_check_for_app_updates(version, result):
    meta.VERSION = version
    assert updater.check_for_app_updates() == result
