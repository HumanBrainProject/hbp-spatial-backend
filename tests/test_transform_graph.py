# Copyright 2019 CEA
# Author: Yann Leprince <yann.leprince@cea.fr>
#
# This file is part of hbp-spatial-backend.
#
# hbp-spatial-backend is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# hbp-spatial-backend is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with hbp-spatial-backend. If not, see <https://www.gnu.org/licenses/>.

import collections
import io

import pytest

from hbp_spatial_backend import transform_graph


def test_transform_graph_sane_usage():
    tg = transform_graph.TransformGraph()
    tg.add_space('A')
    chain = tg.get_transform_chain('A', 'A')
    assert chain == []
    tg.add_space('B')
    chain = tg.get_transform_chain('A', 'B')
    assert chain is None
    tg.add_link('A', 'B', 'Transform A to B')
    chain = tg.get_transform_chain('A', 'B')
    assert chain == ['Transform A to B']
    chain = tg.get_transform_chain('B', 'A')
    assert chain is None
    tg.add_link('B', 'A', 'Transform B to A')
    tg.add_space('C')
    chain = tg.get_transform_chain('A', 'C')
    assert chain is None
    tg.add_link('B', 'C', 'Transform B to C')
    chain = tg.get_transform_chain('A', 'C')
    assert chain == ['Transform A to B', 'Transform B to C']
    tg.remove_link('A', 'B')
    chain = tg.get_transform_chain('A', 'C')
    assert chain is None


def test_transform_graph_cycle():
    tg = transform_graph.TransformGraph()
    # Monkeypatch the tested class to get reliable ordering (with a plain dict
    # Python's hash randomization makes the bug intermittent)
    tg.links = collections.OrderedDict()
    tg.add_space('A')
    tg.add_space('B')
    tg.add_space('C')
    tg.add_link('A', 'B', 'Transform A to B')
    tg.add_link('A', 'C', 'Transform A to C')
    tg.add_link('C', 'A', 'Transform C to A')
    chain = tg.get_transform_chain('A', 'B')
    assert chain == ['Transform A to B']


def test_transform_graph_api_errors():
    tg = transform_graph.TransformGraph()
    tg.add_space('A')
    with pytest.raises(ValueError):
        tg.add_space('A')
    with pytest.raises(KeyError):
        tg.get_transform_chain('A', 'B')
    with pytest.raises(KeyError):
        tg.get_transform_chain('B', 'A')
    tg.add_space('B')
    tg.add_link('A', 'B', 'Transform A to B')
    with pytest.raises(ValueError):
        tg.add_link('A', 'B', 'Duplicate link')


def test_export_graphviz():
    tg = transform_graph.TransformGraph()
    tg.add_space('A')
    tg.add_space('weird"*+chars')
    tg.add_link('A', 'weird"*+chars', 'Transform')
    buf = io.StringIO()
    tg.export_graphviz(buf)
