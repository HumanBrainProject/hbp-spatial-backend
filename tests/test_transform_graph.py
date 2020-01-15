# Copyright 2019–2020 CEA
#
# Author: Yann Leprince <yann.leprince@cea.fr>
#
# Licensed under the Apache Licence, Version 2.0 (the "Licence");
# you may not use this file except in compliance with the Licence.
# You may obtain a copy of the Licence at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the Licence for the specific language governing permissions and
# limitations under the Licence.

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


def test_load_from_yaml():
    tg = transform_graph.TransformGraph.from_yaml(b'{A: {B: AtoB}, B: {}}')
    chain = tg.get_transform_chain('A', 'B')
    assert chain == ['AtoB']
    tg = transform_graph.TransformGraph.from_yaml(b'{A: {B: AtoB}}')
    chain = tg.get_transform_chain('A', 'B')
    assert chain == ['AtoB']
    with pytest.raises(ValueError):
        transform_graph.TransformGraph.from_yaml('[A, B, C]')
