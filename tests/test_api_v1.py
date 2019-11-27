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

import pytest


@pytest.fixture
def test_graph_yaml(tmpdir):
    graph_yaml = str(tmpdir / 'graph.yaml')
    with open(graph_yaml, 'w') as f:
        f.write('{A: {B: identity}, B: {}}')
    return graph_yaml


@pytest.fixture(autouse=True)
def fake_apply_transform(monkeypatch):
    from hbp_spatial_backend import apply_transform

    def transform_points_mock(source_points, transform_chain, cwd=None):
        if transform_chain == ['identity']:
            return [tuple(point) for point in source_points]
        raise RuntimeError('Unexpected call')

    monkeypatch.setattr(apply_transform, 'transform_points',
                        transform_points_mock)


def test_transform_point_request_validation(app, client, test_graph_yaml):
    app.config['DEFAULT_TRANSFORM_GRAPH'] = test_graph_yaml
    response = client.get('/v1/transform-point')
    assert response.status_code == 400
    response = client.get('/v1/transform-point',
                          query_string={'source_space': 'A',
                                        'target_space': 'B',
                                        'x': 1, 'y': 2, 'z': 3.5})
    assert response.status_code == 200
    assert response.json == {'target_point': [1, 2, 3.5]}

    response = client.get('/v1/transform-point',
                          query_string={'source_space': 'A',
                                        'target_space': 'B'})
    assert response.status_code == 400

    response = client.get('/v1/transform-point',
                          query_string={'x': 1, 'y': 2, 'z': 3,
                                        'target_space': 'B'})
    assert response.status_code == 400

    response = client.get('/v1/transform-point',
                          query_string={'x': 1, 'y': 2, 'z': 3,
                                        'source_space': 'A'})
    assert response.status_code == 400

    response = client.get('/v1/transform-point',
                          query_string={'x': 1, 'y': 2, 'z': 3,
                                        'source_space': 'A',
                                        'target_space': 'nonexistent'})
    assert response.status_code == 400

    response = client.get('/v1/transform-point',
                          query_string={'x': 1, 'y': 2, 'z': 3,
                                        'source_space': 'nonexistent',
                                        'target_space': 'B'})
    assert response.status_code == 400


def test_transform_points_request_validation(app, client, test_graph_yaml):
    app.config['DEFAULT_TRANSFORM_GRAPH'] = test_graph_yaml

    response = client.get('/v1/transform-points')
    assert response.status_code == 405

    response = client.post('/v1/transform-points', json={
        'source_space': 'A',
        'target_space': 'B',
        'points': [
            [1, 2, 3.5],
            [0, -1, 0.5],
        ],
    })
    assert response.status_code == 200
    assert response.json == {
        'target_points': [
            [1, 2, 3.5],
            [0, -1, 0.5],
        ],
    }

    # TODO: test response to other kinds of malformed requests
