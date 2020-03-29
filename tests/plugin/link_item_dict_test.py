from datetime import datetime

import pytest

from unidown.plugin.link_item import LinkItem
from unidown.plugin.link_item_dict import LinkItemDict

eg_data = LinkItemDict({
    '/IceflowRE/unidown/master/README.rst': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
    '/IceflowRE/unidown/master/LICENSE.md': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
    '/IceflowRE/unidown/master/missing': LinkItem('missing', datetime(2002, 2, 2, hour=2, minute=2, second=2))
})

test_data = [
    (LinkItemDict(), LinkItemDict(), LinkItemDict()),
    (LinkItemDict(), eg_data, eg_data),
    (eg_data, LinkItemDict(), eg_data),
    (
        LinkItemDict({'/IceflowRE/unidown/master/README.rst': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1))}),
        LinkItemDict({
            '/IceflowRE/unidown/master/LICENSE.md': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
            '/IceflowRE/unidown/master/missing': LinkItem('missing', datetime(2002, 2, 2, hour=2, minute=2, second=2))
        }),
        eg_data
    )
]


@pytest.mark.parametrize('base,new_data,result', test_data)
def test_actualize(base, new_data, result):
    base.actualize(new_data)
    assert base == result


test_data = [
    (LinkItemDict(), LinkItemDict(), LinkItemDict()),
    (LinkItemDict(), eg_data, eg_data),
    (eg_data, LinkItemDict(), LinkItemDict()),
    (
        LinkItemDict({'/IceflowRE/unidown/master/README.rst': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1))}),
        LinkItemDict({
            '/IceflowRE/unidown/master/README.rst': LinkItem('othername.md', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
            '/IceflowRE/unidown/master/missing': LinkItem('missing', datetime(2002, 2, 2, hour=2, minute=2, second=2))
        }),
        LinkItemDict({'/IceflowRE/unidown/master/missing': LinkItem('missing', datetime(2002, 2, 2, hour=2, minute=2, second=2))})
    ),
    (eg_data, LinkItemDict({'/IceflowRE/unidown/master/README.rst': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1))}), LinkItemDict())
]


@pytest.mark.parametrize('old_data,new_data,result', test_data)
def test_get_new_items(old_data, new_data, result):
    assert LinkItemDict.get_new_items(old_data, new_data) == result


def test_clean_up_names():
    eg_data = LinkItemDict({
        '/IceflowRE/unidown/master/README.rst': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
        '/IceflowRE/unidown/master/LICENSE.md': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
        '/IceflowRE/unidown/master/missing': LinkItem('missing', datetime(2002, 2, 2, hour=2, minute=2, second=2))
    })
    eg_data.clean_up_names()
    assert eg_data == LinkItemDict({
        '/IceflowRE/unidown/master/README.rst': LinkItem('README_d.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
        '/IceflowRE/unidown/master/LICENSE.md': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
        '/IceflowRE/unidown/master/missing': LinkItem('missing', datetime(2002, 2, 2, hour=2, minute=2, second=2))
    })
