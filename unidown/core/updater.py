"""
Things needed for checking for updates.
"""

import certifi
import urllib3
from packaging import version

from unidown import static_data


def get_newest_app_version() -> str:
    """
    Download the version tag from remote. TODO: versionurl.

    :return: version from remote
    :rtype: str
    """
    with urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()) as p_man:
        online_version = p_man.urlopen('GET', static_data.VERSION_URL).data.decode('utf-8')
    return online_version


def check_for_app_updates() -> bool:
    """
    Check for updates.

    :return: is update available
    :rtype: bool
    """
    online_version = get_newest_app_version()
    return version.parse(online_version) > version.parse(static_data.VERSION)  # TODO: catch invalid version
