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
import requests


@pytest.fixture
def base_url():
    return 'https://hbp-spatial-backend.apps.hbp.eu/'
    # return 'https://hbp-spatial-backend.apps-dev.hbp.eu/'
    # return 'http://localhost:5000/'


class TransformRequester:
    def __init__(self, base_url):
        self.base_url = base_url

    def transform(self, source_space, target_space, points):
        r = requests.post(self.base_url + 'v1/transform-points',
                          json={
                              'source_space': source_space,
                              'target_space': target_space,
                              'source_points': points,
                          }, headers={
                              'Cache-Control': 'no-cache',
                          })
        r.raise_for_status()
        response_body = r.json()
        return [
            (x, y, z) for (x, y, z) in response_body['target_points']
        ]


@pytest.fixture
def transform_requester(base_url):
    return TransformRequester(base_url)


def points_approx_equal(test_points, reference_points, tol=0.1):
    for test_point, reference_point in zip(test_points, reference_points):
        return all(abs(t - r) < tol
                   for t, r in zip(test_point, reference_point))


def test_health(base_url):
    r = requests.get(base_url + 'health',
                     headers={
                         'Cache-Control': 'no-cache',
                     })
    assert r.status_code == 200


# Shorthands
MNI152 = 'MNI 152 ICBM 2009c Nonlinear Asymmetric'
COLIN27 = 'MNI Colin 27'
BIGBRAIN = 'Big Brain (Histology)'
INFANT = 'Infant Atlas'

TEST_POINTS_FOR_TEMPLATE = {
    # All the templates can be tested with the default points (below)
}


@pytest.mark.parametrize('source_space,intermediate_space', [
    (MNI152, BIGBRAIN),
    (BIGBRAIN, COLIN27),
    (COLIN27, INFANT),
    (INFANT, MNI152),
])
def test_roundtrip(transform_requester, source_space, intermediate_space):
    # Default test points
    orig_points = TEST_POINTS_FOR_TEMPLATE.get(source_space, [
        (0, 0, 0),
        (10, 0, 0),
        (0, 10, 0),
    ])
    intermediate_points = transform_requester.transform(
        source_space, intermediate_space, orig_points)
    roundtripped_points = transform_requester.transform(
        intermediate_space, source_space, intermediate_points)
    assert points_approx_equal(roundtripped_points, orig_points)
