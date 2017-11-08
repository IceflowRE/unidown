"""
Things needed for checking for updates.
"""

import certifi
import urllib3
from packaging import version

import unidown.core.data.static as static_data


def get_newest_app_version():
    """
    Download the version tag from Github and returns as list.
    :return: [year, month, day, ...]
    """
    with urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()) as p_man:
        version = p_man.urlopen('GET', static_data.VERSION_URL).data.decode('utf-8')
    return version


def check_for_app_updates():
    """
    Check for updates.
    :return: boolean: if an update is available
    """
    online_version = get_newest_app_version()
    return version.parse(online_version) > version.parse(static_data.VERSION)
