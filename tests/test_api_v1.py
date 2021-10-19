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

import pytest


@pytest.fixture
def dummy_graph_yaml(tmpdir):
    graph_yaml = str(tmpdir / 'graph.yaml')
    with open(graph_yaml, 'w') as f:
        f.write('{A: {B: A_to_B}, B: {A: B_to_A}}')
    return graph_yaml


@pytest.fixture(autouse=True)
def fake_apply_transform(monkeypatch):
    from hbp_spatial_backend import apply_transform

    def transform_points_mock(source_points, transform_chain, cwd=None):
        if transform_chain in (['A_to_B'], ['B_to_A']):
            return [tuple(point) for point in source_points]
        raise RuntimeError('Unexpected call')

    monkeypatch.setattr(apply_transform, 'transform_points',
                        transform_points_mock)


def test__get_transform_graph(app, dummy_graph_yaml):
    from hbp_spatial_backend import api_v1
    app.config['DEFAULT_TRANSFORM_GRAPH'] = dummy_graph_yaml
    with app.test_request_context():
        tg1 = api_v1._get_transform_graph()
        tg2 = api_v1._get_transform_graph()
    assert tg1 is tg2  # test that the graph is only loaded once per request


def test_get_graph_yaml(app, client, dummy_graph_yaml):
    app.config['DEFAULT_TRANSFORM_GRAPH'] = dummy_graph_yaml
    response = client.get('/v1/graph.yaml')
    assert response.status_code == 200
    with open(dummy_graph_yaml, 'rt') as f:
        graph_yaml_contents = f.read()
    assert response.get_data(as_text=True) == graph_yaml_contents


def test_transform_point_request_validation(app, client, dummy_graph_yaml):
    app.config['DEFAULT_TRANSFORM_GRAPH'] = dummy_graph_yaml
    response = client.get('/v1/transform-point')
    assert response.status_code == 422
    response = client.get('/v1/transform-point',
                          query_string={'source_space': 'A',
                                        'target_space': 'B',
                                        'x': 1, 'y': 2, 'z': 3.5})
    assert response.status_code == 200
    assert response.json == {'target_point': [1, 2, 3.5]}

    response = client.get('/v1/transform-point',
                          query_string={'source_space': 'A',
                                        'target_space': 'B'})
    assert response.status_code == 422

    response = client.get('/v1/transform-point',
                          query_string={'x': 1, 'y': 2, 'z': 3,
                                        'target_space': 'B'})
    assert response.status_code == 422

    response = client.get('/v1/transform-point',
                          query_string={'x': 1, 'y': 2, 'z': 3,
                                        'source_space': 'A'})
    assert response.status_code == 422

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


def test_transform_points_request_validation(app, client, dummy_graph_yaml):
    app.config['DEFAULT_TRANSFORM_GRAPH'] = dummy_graph_yaml

    response = client.get('/v1/transform-points')
    assert response.status_code == 405

    response = client.post('/v1/transform-points', json={
        'source_space': 'A',
        'target_space': 'B',
        'source_points': [
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

    response = client.post('/v1/transform-points', json={
        'source_space': 'nonexistent',
        'target_space': 'B',
        'source_points': [
            [1, 2, 3.5],
        ],
    })
    assert response.status_code == 400

    response = client.post('/v1/transform-points', json={
        'source_space': 'A',
        'target_space': 'B'
    })
    assert response.status_code == 422


def test_get_mesh_transform_command(app, client, dummy_graph_yaml):
    app.config['DEFAULT_TRANSFORM_GRAPH'] = dummy_graph_yaml
    response = client.get('/v1/get-mesh-transform-command')
    assert response.status_code == 422
    response = client.get('/v1/get-mesh-transform-command',
                          query_string={'source_space': 'A',
                                        'target_space': 'B'})
    assert response.status_code == 200
    assert 'transform_command' in response.json
    assert response.json['transform_command'][0] == 'AimsApplyTransform'
    txt_cmd = ' '.join(response.json['transform_command'])
    assert '--input-coords auto' in txt_cmd
    assert '--direct-transform A_to_B' in txt_cmd

    response = client.get('/v1/get-mesh-transform-command',
                          query_string={'source_space': 'A',
                                        'target_space': 'nonexistent'})
    assert response.status_code == 400

    response = client.get('/v1/get-mesh-transform-command',
                          query_string={'source_space': 'nonexistent',
                                        'target_space': 'B'})
    assert response.status_code == 400


@pytest.fixture
def dummy_image_graph_yaml(tmpdir):
    graph_yaml = str(tmpdir / 'graph.yaml')
    with open(graph_yaml, 'w') as f:
        f.write('''\
{
  A: {Aimg: A_to_Aimg},
  Aimg: {A: Aimg_to_A, Bimg: Aimg_to_Bimg},
  Bimg: {B: Bimg_to_B, Aimg: Bimg_to_Aimg},
  B: {Bimg: B_to_Bimg},
}
''')
    return graph_yaml


def test_get_image_transform_command(app, client,
                                     dummy_image_graph_yaml):
    app.config['DEFAULT_TRANSFORM_GRAPH'] = dummy_image_graph_yaml
    response = client.get('/v1/get-image-transform-command')
    assert response.status_code == 422
    response = client.get('/v1/get-image-transform-command',
                          query_string={'source_space': 'A',
                                        'target_space': 'B'})
    assert response.status_code == 200
    assert 'transform_command' in response.json
    assert response.json['transform_command'][0] == 'AimsApplyTransform'
    txt_cmd = ' '.join(response.json['transform_command'])
    assert '--input-coords auto' in txt_cmd
    assert ('--inverse-transform Bimg_to_Aimg '
            '--inverse-transform Aimg_to_A'
            in txt_cmd)
    assert '--reference Bimg_to_Aimg' in txt_cmd

    response = client.get('/v1/get-image-transform-command',
                          query_string={'source_space': 'A',
                                        'target_space': 'nonexistent'})
    assert response.status_code == 400

    response = client.get('/v1/get-image-transform-command',
                          query_string={'source_space': 'nonexistent',
                                        'target_space': 'B'})
    assert response.status_code == 400
