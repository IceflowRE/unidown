from __future__ import annotations

import logging
from pathlib import Path

from tqdm import tqdm


class LinkItemDict(dict):
    """
    LinkItem dictionary, acts as a wrapper for special methods and functions.
    """

    def actualize(self, new_data: LinkItemDict, log: logging.Logger = None):
        """
        Actualize dictionary like an ~dict.update does.
        If a logger is passed it will log updated items, **not** new one.

        :param new_data: the data used for updating
        :param log: logger
        """
        if log is not None:
            for link, item in new_data.items():
                if link in self.keys():
                    log.info(f"Actualize item: {link} | {self[link]} -> {item}")
        self.update(new_data)

    def clean_up_names(self):
        """
        Rename duplicated names with an additional ``_r``.
        """
        for cur_link, cur_item in self.items():
            restart = True
            while restart:
                restart = False
                for link, item in self.items():
                    if cur_item.name == item.name and cur_link != link:
                        tmp = Path(cur_item.name)
                        cur_item.name = f"{tmp.stem}_d{''.join(tmp.suffixes)}"
                        restart = True
                        break

    @staticmethod
    def get_new_items(old_data: LinkItemDict, new_data: LinkItemDict, disable_tqdm: bool = False) -> LinkItemDict:
        """
        Get the new items which are not existing or are newer as in the old data set.

        :param old_data: old data
        :param new_data: new data
        :param disable_tqdm: disables tqdm progressbar
        :return: new and updated link items
        """
        if len(old_data) == 0:
            return new_data
        if len(new_data) == 0:
            return LinkItemDict()

        updated_data = LinkItemDict()
        for link, link_item in tqdm(new_data.items(), desc="Compare with save", unit="item", mininterval=1, ncols=100, disable=disable_tqdm):
            if (link not in old_data) or (link_item.time > old_data[link].time):
                updated_data[link] = link_item

        return updated_data
