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
import io
import logging
import unittest.mock

import pytest

from hbp_spatial_backend import apply_transform
from hbp_spatial_backend.apply_transform import parse_points_output


def test_parse_points_output():
    res = list(parse_points_output(io.StringIO('')))
    assert res == []
    # space before comma is intentional (was the format of AIMS < 4.6)
    res = list(parse_points_output(io.StringIO('(1, 2 ,3)')))
    assert res == [(1, 2, 3)]
    res = list(parse_points_output(io.StringIO('(1e-1, 0.2, -3.5e2)')))
    assert res == [(1e-1, 0.2, -3.5e2)]
    # Test trailing newline
    res = list(parse_points_output(io.StringIO('(1, 2 ,3)\n')))
    assert res == [(1, 2, 3)]
    # Test discarding garbage
    res = list(parse_points_output(io.StringIO('garbage\n(1, 2 ,3)\n')))
    assert res == [(1, 2, 3)]


@unittest.mock.patch('subprocess.run', autospec=True)
def test_transform_point(subprocess_run_mock, app):
    class CompletedProcessMock:
        def __init__(self):
            self.stdout = '(1.4 ,-2.5 ,1e-3)'
    subprocess_run_mock.return_value = CompletedProcessMock()
    with app.app_context():
        res = apply_transform.transform_point(
            (1.1, -2.2, 3e1),
            ['A.ima', 'B.trm'],
            cwd='toto',
        )

    assert subprocess_run_mock.called
    args, kwargs = subprocess_run_mock.call_args
    cmd = args[0]
    assert cmd[0] == 'AimsApplyTransform'
    assert '--points' in cmd
    txt_cmd = ' '.join(cmd)
    assert '--input -' in txt_cmd
    assert '--output -' in txt_cmd
    assert '--direct-transform A.ima --direct-transform B.trm' in txt_cmd
    assert kwargs['check'] is True
    assert kwargs['cwd'] == 'toto'
    assert kwargs['universal_newlines'] is True
    assert list(apply_transform.parse_points_output(
        io.StringIO(kwargs['input']))) == [(1.1, -2.2, 30)]
    assert res == (1.4, -2.5, 1e-3)


@unittest.mock.patch('subprocess.run', autospec=True)
def test_transform_points(subprocess_run_mock, app, caplog):
    class CompletedProcessMock:
        # space before comma is intentional (was the behaviour of AIMS < 4.6)
        stdout = '(4, 5 ,6)\n(-7,-8 , -9.5)'

    subprocess_run_mock.return_value = CompletedProcessMock()
    with app.app_context():
        with caplog.at_level(logging.DEBUG,
                             logger='hbp_spatial_backend.apply_transform'):
            res = apply_transform.transform_points(
                [(1, 2, 3), (4, 5, 6)],
                ['A.ima', 'B.trm'],
                cwd='toto',
            )

    assert subprocess_run_mock.called
    args, kwargs = subprocess_run_mock.call_args
    cmd = args[0]
    assert cmd[0] == 'AimsApplyTransform'
    assert '--points' in cmd
    txt_cmd = ' '.join(cmd)
    assert '--input -' in txt_cmd
    assert '--output -' in txt_cmd
    assert '--direct-transform A.ima --direct-transform B.trm' in txt_cmd
    assert kwargs['check'] is True
    assert kwargs['cwd'] == 'toto'
    assert kwargs['universal_newlines'] is True
    assert list(apply_transform.parse_points_output(
        io.StringIO(kwargs['input']))) == [(1, 2, 3), (4, 5, 6)]
    assert res == [(4, 5, 6), (-7, -8, -9.5)]


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
