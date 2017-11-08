"""
Different tools.
"""

from concurrent.futures import as_completed
from datetime import datetime
from pathlib import Path

from google.protobuf.timestamp_pb2 import Timestamp
from tqdm import tqdm

import unidown.core.data.dynamic as dynamic_data
from unidown.tools.tdqm_option import TdqmOption


def progress_bar(job_list, option: TdqmOption):
    """
    Progress bar for the downloaded future objects.
    :param job_list: job_list which will be downloaded
    :param option: Tqdm options
    :return: progress bar
    """
    pbar = tqdm(as_completed(job_list), total=len(job_list), desc=option.desc, unit=option.unit, leave=True,
                mininterval=1, ncols=100, disable=dynamic_data.DISABLE_TQDM)
    for iteration in pbar:
        pass

    return pbar


def delete_dir_rec(path: Path):
    """
    Delete a folder recursive.
    :param path: folder to deleted
    """
    if not path.exists() or not path.is_dir():
        return
    for sub in path.iterdir():
        if sub.is_dir():
            delete_dir_rec(sub)
        else:
            sub.unlink()
    path.rmdir()


def create_dir_rec(path: Path):
    """
    Create a folder recursive.
    :param path: path
    """
    if not path.exists():
        Path.mkdir(path, parents=True)


def datetime_to_timestamp(time: datetime):
    """
    Convert datetime to protobuf.timestamp.
    :param time: time
    :return: protobuf.timestamp object
    """
    protime = Timestamp()
    protime.FromDatetime(time)
    return protime
