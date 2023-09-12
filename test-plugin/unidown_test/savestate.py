from datetime import datetime
from typing import Self

from unidown.plugin.link_item_dict import LinkItemDict
from unidown.plugin.plugin_info import PluginInfo
from unidown.plugin.savestate import SaveState


class MySaveState(SaveState):
    """
    TestPlugins customized SaveState.
    """

    def __init__(self, plugin_info: PluginInfo, last_update: datetime, link_items: LinkItemDict, username: str = ''):
        super().__init__(plugin_info, last_update, link_items)
        self.username: str = username

    @classmethod
    def from_json(cls, data: dict) -> Self:
        savestate = super(MySaveState, cls).from_json(data)
        if 'username' in data:
            savestate.username = data['username']
        return savestate

    def to_json(self) -> dict:
        data = super().to_json()
        data['username'] = self.username
        return data

    def upgrade(self) -> Self:
        new_savestate = super(MySaveState, self).upgrade()
        new_savestate.username = self.username
        return new_savestate
