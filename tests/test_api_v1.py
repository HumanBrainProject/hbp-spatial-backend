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


def test_transform_point_request_validation(client):
    response = client.get('/v1/transform-point',
                          content_type='application/json')
    assert response.status_code == 400
    response = client.get('/v1/transform-point',
                          json={'source_point': [1, 2, 3],
                                'source_space': 'A',
                                'target_space': 'B'})
    assert response.status_code == 200
    assert response.json == {'target_point': [1, 2, 3]}

    response = client.get('/v1/transform-point',
                          json={'source_space': 'A',
                                'target_space': 'B'})
    assert response.status_code == 400

    response = client.get('/v1/transform-point',
                          json={'source_point': [1, 2, 3],
                                'target_space': 'B'})
    assert response.status_code == 400

    response = client.get('/v1/transform-point',
                          json={'source_point': [1, 2, 3],
                                'source_space': 'A'})
    assert response.status_code == 400

    response = client.get('/v1/transform-point',
                          json={'source_point': [1, 2],
                                'source_space': 'A',
                                'target_space': 'B'})
    assert response.status_code == 400
