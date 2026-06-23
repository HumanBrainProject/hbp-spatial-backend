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
from subprocess import CalledProcessError


@pytest.fixture
def dummy_graph_yaml(tmpdir):
    graph_yaml = str(tmpdir / 'graph.yaml')
    with open(graph_yaml, 'w') as f:
        f.write('{A: {B: A_to_B}, B: {A: B_to_A}}')
    return graph_yaml


@pytest.fixture(autouse=True)
def fake_apply_transform(monkeypatch):
    from hbp_spatial_backend import apply_transform

    def transform_points_mock(source_points, input_space, output_space, graph,
                              cwd=None):
        if (input_space, output_space) in (('A', 'B'), ('B', 'A')):
            return [tuple(point) for point in source_points]
        raise CalledProcessError(1, "", None, f'Unexpected call, {source_points}, {input_space}, {output_space}')

    def transform_point_mock(source_point, input_space, output_space, graph,
                              cwd=None):
        if (input_space, output_space) in (('A', 'B'), ('B', 'A')):
            return tuple(source_point)
        raise CalledProcessError(1, "", None, f'Unexpected call, {input_space}, {output_space}')

    monkeypatch.setattr(apply_transform, 'transform_points',
                        transform_points_mock)
    monkeypatch.setattr(apply_transform, 'transform_point',
                        transform_point_mock)


def test_get_graph_yaml(app, client, dummy_graph_yaml):
    app.config['DEFAULT_TRANSFORM_GRAPH'] = dummy_graph_yaml
    response = client.get('/v1/graph.yaml')
    assert response.status_code == 200
    with open(dummy_graph_yaml, 'rt') as f:
        graph_yaml_contents = f.read()
    assert response.get_data(as_text=True) == graph_yaml_contents


@pytest.mark.parametrize(
    "query_string, expected_status_code, expected_json",
    [
        ({}, 422, None),
        (
            {"source_space": "A", "target_space": "B", "x": 1, "y": 2, "z": 3.5},
            200,
            {"target_point": [1, 2, 3.5]},
        ),
        ({"source_space": "A", "target_space": "B"}, 422, None),
        ({"x": 1, "y": 2, "z": 3, "target_space": "B"}, 422, None),
        ({"x": 1, "y": 2, "z": 3, "source_space": "A"}, 422, None),
        (
            {
                "x": 1,
                "y": 2,
                "z": 3,
                "source_space": "A",
                "target_space": "nonexistent",
            },
            400,
            None,
        ),
        (
            {
                "x": 1,
                "y": 2,
                "z": 3,
                "source_space": "nonexistent",
                "target_space": "B",
            },
            400,
            None,
        ),
    ],
)
def test_transform_point_request_validation(
    app, client, dummy_graph_yaml, query_string, expected_status_code, expected_json
):
    app.config["DEFAULT_TRANSFORM_GRAPH"] = dummy_graph_yaml
    response = client.get("/v1/transform-point", query_string=query_string)
    assert response.status_code == expected_status_code
    if expected_json is not None:
        assert response.json == expected_json


@pytest.mark.parametrize(
    "method, json, expected_status_code, expected_json",
    [
        ("GET", None, 405, None),
        (
            "POST",
            {
                "source_space": "A",
                "target_space": "B",
                "source_points": [
                    [1, 2, 3.5],
                    [0, -1, 0.5],
                ],
            },
            200,
            {
                "target_points": [
                    [1, 2, 3.5],
                    [0, -1, 0.5],
                ],
            },
        ),
        (
            "POST",
            {
                "source_space": "nonexistent",
                "target_space": "B",
                "source_points": [
                    [1, 2, 3.5],
                ],
            },
            400,
            None,
        ),
        (
            "POST",
            {"source_space": "A", "target_space": "B"},
            422,
            None,
        ),
    ],
)
def test_transform_points_request_validation(
    app, client, dummy_graph_yaml, method, json, expected_status_code, expected_json
):
    app.config["DEFAULT_TRANSFORM_GRAPH"] = dummy_graph_yaml
    response = client.open("/v1/transform-points", method=method, json=json)
    assert response.status_code == expected_status_code
    if expected_json is not None:
        assert response.json == expected_json


# TODO get_image_transform_command is not used in prod
# there seems to be an update of AIMS API?
# double check how this functionality can be checked

# def test_get_mesh_transform_command(app, client, dummy_graph_yaml):
#     app.config['DEFAULT_TRANSFORM_GRAPH'] = dummy_graph_yaml
#     response = client.get('/v1/get-mesh-transform-command')
#     assert response.status_code == 422
#     response = client.get('/v1/get-mesh-transform-command',
#                           query_string={'source_space': 'A',
#                                         'target_space': 'B'})
#     assert response.status_code == 200
#     assert 'transform_command' in response.json
#     assert response.json['transform_command'][0] == 'AimsApplyTransform'
#     txt_cmd = ' '.join(response.json['transform_command'])
#     assert '--input-coords auto' in txt_cmd
#     assert '--direct-transform A_to_B' in txt_cmd

#     response = client.get('/v1/get-mesh-transform-command',
#                           query_string={'source_space': 'A',
#                                         'target_space': 'nonexistent'})
#     assert response.status_code == 400

#     response = client.get('/v1/get-mesh-transform-command',
#                           query_string={'source_space': 'nonexistent',
#                                         'target_space': 'B'})
#     assert response.status_code == 400


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


# TODO get_image_transform_command is not used in prod
# there seems to be an update of AIMS API?
# double check how this functionality can be checked

# def test_get_image_transform_command(app, client,
#                                      dummy_image_graph_yaml):
#     app.config['DEFAULT_TRANSFORM_GRAPH'] = dummy_image_graph_yaml
#     response = client.get('/v1/get-image-transform-command')
#     assert response.status_code == 422
#     response = client.get('/v1/get-image-transform-command',
#                           query_string={'source_space': 'A',
#                                         'target_space': 'B'})
#     assert response.status_code == 200
#     assert 'transform_command' in response.json
#     assert response.json['transform_command'][0] == 'AimsApplyTransform'
#     txt_cmd = ' '.join(response.json['transform_command'])
#     assert '--input-coords auto' in txt_cmd
#     assert ('--inverse-transform Bimg_to_Aimg '
#             '--inverse-transform Aimg_to_A'
#             in txt_cmd)
#     assert '--reference Bimg_to_Aimg' in txt_cmd

#     response = client.get('/v1/get-image-transform-command',
#                           query_string={'source_space': 'A',
#                                         'target_space': 'nonexistent'})
#     assert response.status_code == 400

#     response = client.get('/v1/get-image-transform-command',
#                           query_string={'source_space': 'nonexistent',
#                                         'target_space': 'B'})
#     assert response.status_code == 400
