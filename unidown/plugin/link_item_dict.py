from __future__ import annotations

import logging

from tqdm import tqdm


class LinkItemDict(dict):
    """
    LinkItem dictionary, acts as a wrapper for special methods and functions.
    """

    def actualize(self, new_data: LinkItemDict, log: logging.Logger = None):
        """
        Actualize dictionary like an ~dict.update does. Additionally adds logging support.

        :param new_data: the data used for udpating
        :param log: logger
        """
        if log is not None:
            for link, item in new_data.items():
                if link in super().keys():
                    log.info('Actualize item: ' + link + ' | ' + str(self[link]) + ' -> ' + str(item))
        self.update(new_data)

    @staticmethod
    def get_new_items(old_data: LinkItemDict, new_data: LinkItemDict, disable_tqdm: bool = False) -> LinkItemDict:
        """
        Get the new items which are not existing or are newer as in the old data set.

        :param old_data: old data
        :param new_data: new data
        :param disable_tqdm: disables tqdm progressbar
        :return: new and updated link items
        """
        if not old_data:
            return new_data
        if not new_data:
            return LinkItemDict()

        updated_data = LinkItemDict()
        for link, link_item in tqdm(new_data.items(), desc="Compare with save", unit="item", mininterval=1, ncols=100, disable=disable_tqdm):
            if (link not in old_data) or (link_item.time > old_data[link].time):
                updated_data[link] = link_item

        return updated_data
