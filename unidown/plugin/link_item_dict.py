from __future__ import annotations

import logging

from tqdm import tqdm

from unidown import dynamic_data


class LinkItemDict(dict):
    def actualize(self, new_data: LinkItemDict, log: logging.Logger = None):
        if log is not None:
            for link, item in new_data.items():
                if link in super():
                    log.info('Actualize item: ' + link + ' | ' + str(self[link]) + ' -> ' + str(item))
        self.update(new_data)

    @staticmethod
    def get_new_items(old_data: LinkItemDict, new_data: LinkItemDict) -> LinkItemDict:
        if not old_data:
            return new_data
        if not new_data:
            return LinkItemDict()

        updated_data = LinkItemDict()
        for link, link_item in tqdm(new_data.items(), desc="Compare with save", unit="item", leave=True, mininterval=1,
                                    ncols=100, disable=dynamic_data.DISABLE_TQDM):
            if (link not in old_data) or (link_item.time > old_data[link].time):
                updated_data[link] = link_item

        return updated_data
