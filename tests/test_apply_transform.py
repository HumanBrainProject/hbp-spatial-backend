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

from distutils.spawn import find_executable

import pytest

from hbp_spatial_backend import apply_transform


@pytest.mark.skipif(find_executable('AimsApplyTransform') is None,
                    reason='AimsApplyTransform not found on PATH')
def test_call_transform_point():
    res = apply_transform.transform_point([1, 2, 3], [])
    assert res == (1, 2, 3)
