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

from distutils.spawn import find_executable
import io
import logging
import unittest.mock

import pytest

from hbp_spatial_backend import apply_transform


@pytest.mark.skipif(find_executable('AimsApplyTransform') is None,
                    reason='AimsApplyTransform not found on PATH')
def test_AimsApplyTransform(app):
    with app.app_context():
        res = apply_transform.transform_point([1, 2, 3], [])
    assert res == (1, 2, 3)


@pytest.mark.skipif(find_executable('AimsApplyTransform') is None,
                    reason='AimsApplyTransform not found on PATH')
def test_AimsApplyTransform_with_trm(tmpdir, app):
    test_trm = str(tmpdir / 'test.trm')
    with open(test_trm, 'w') as f:
        f.write('0 0 0\n-1 0 0\n0 -1 0\n0 0 -1\n')
    with app.app_context():
        res = apply_transform.transform_point([1, 2, 3], [test_trm])
    assert res == (-1, -2, -3)
