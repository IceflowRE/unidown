"""
Things needed for checking for updates.
"""
import json

import certifi
import urllib3
from packaging.version import Version

from unidown import meta


def get_newest_app_version() -> Version:
    """
    Download the version tag from remote.

    :return: Version from remote.
    """
    with urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()) as p_man:
        pypi_json = p_man.urlopen('GET', meta.PYPI_JSON_URL).data.decode('utf-8')
    releases = json.loads(pypi_json).get('releases', [])
    online_version = Version('0.0.0')
    for release in releases:
        cur_version = Version(release)
        if not cur_version.is_prerelease:
            online_version = max(online_version, cur_version)
    return online_version


def check_for_app_updates() -> bool:
    """
    Check for updates.

    :return: Is update available.
    """
    return get_newest_app_version() > Version(meta.VERSION)
