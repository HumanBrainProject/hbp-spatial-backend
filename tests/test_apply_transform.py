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


def test_get_transform_command(app):
    with app.app_context():
        cmd = apply_transform.get_transform_command(
            ['A.ima', 'B.trm'],
            ['inv:B.ima', 'inv:A.trm'],
            reference='reference.nii',
            input_coords='auto',
        )

    assert cmd[0] == 'AimsApplyTransform'
    txt_cmd = ' '.join(cmd)
    assert '--direct-transform A.ima --direct-transform B.trm' in txt_cmd
    assert ('--inverse-transform inv:B.ima --inverse-transform inv:A.trm'
            in txt_cmd)
    assert '--reference reference.nii' in txt_cmd
    assert '--input-coords auto' in txt_cmd

    with app.app_context():
        cmd = apply_transform.get_transform_command(
            ['A.ima', 'B.trm'],
        )
    assert cmd[0] == 'AimsApplyTransform'
    txt_cmd = ' '.join(cmd)
    assert '--direct-transform A.ima --direct-transform B.trm' in txt_cmd
    assert '--inverse-transform' not in cmd
    assert '--reference' not in cmd
    assert '--input-coords' not in cmd


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
