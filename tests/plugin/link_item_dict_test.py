from datetime import datetime

import pytest

from unidown.plugin.link_item import LinkItem
from unidown.plugin.link_item_dict import LinkItemDict

eg_data = LinkItemDict({
    'one': LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
    'two': LinkItem('Two', datetime(2002, 2, 2, hour=2, minute=2, second=2)),
})

test_data = [
    (LinkItemDict(), LinkItemDict(), LinkItemDict()),
    (LinkItemDict(), eg_data, eg_data),
    (eg_data, LinkItemDict(), LinkItemDict()),
    (
        LinkItemDict({'one': LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1))}),
        eg_data,
        LinkItemDict({'two': LinkItem('Two', datetime(2002, 2, 2, hour=2, minute=2, second=2))}),
    ),
    (eg_data, LinkItemDict({'one': LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1))}), LinkItemDict()),
]


@pytest.mark.parametrize('old_data,new_data,result', test_data)
def test_get_new_items(old_data, new_data, result):
    assert LinkItemDict.get_new_items(old_data, new_data) == result
