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

import io
import logging
import re
import subprocess
import time

from flask import current_app


logger = logging.getLogger(__name__)


def transform_points(source_points, direct_transform_chain, cwd=None):
    transform_params = []
    for t in direct_transform_chain:
        transform_params.extend(['--direct-transform', t])
    cmd = [
        'AimsApplyTransform',
        '--points',
        '--mmap-fields',
        '--input', '-',
        '--output', '-'
    ] + transform_params
    input_points_str = '\n'.join(
        '({0}, {1}, {2})'.format(*p) for p in source_points
    )
    # if logger.isEnabledFor(logging.DEBUG):
    import shlex
    logger.info('Transforming %d points with: %s', len(source_points),
                ' '.join(shlex.quote(arg) for arg in cmd))
    logger.info(' '.join(cmd))
    time_before = time.perf_counter()

    res = subprocess.run(
        cmd,
        check=True,
        input=input_points_str,
        stdout=subprocess.PIPE,
        universal_newlines=True,  # synonym of text=True for Python < 3.7
        cwd=cwd,
        timeout=current_app.config['REQUEST_TIMEOUT'],
    )
    elapsed_time = time.perf_counter() - time_before
    logger.info('AimsApplyTransform completed in %.3f s', elapsed_time)
    target_points = list(parse_points_output(io.StringIO(res.stdout)))
    assert len(target_points) == len(source_points)
    return target_points


def get_transform_command(input_coords,
                          direct_transform_chain,
                          inverse_transform_chain):
    transform_params = []
    for t in direct_transform_chain:
        transform_params.extend(['--direct-transform', t])
    for t in inverse_transform_chain:
        transform_params.extend(['--inverse-transform', t])

    cmd = ['AimsApplyTransform']
    cmd.extend(['--input-coords', input_coords])
    cmd.extend(transform_params)

    return cmd


def transform_point(source_point, direct_transform_chain, cwd=None):
    target_points = transform_points([source_point],
                                     direct_transform_chain,
                                     cwd=cwd)
    assert len(target_points) == 1
    return target_points[0]


def parse_points_output(stdout_stream):
    """Parse a list of points in the format output by AimsApplyTransform.

    This is a generator that yields 3-tuples of Floats.
    """
    POINT_RE = re.compile(r'^\s*\(\s*([^,]+)\s*,'
                          r'\s*([^,]+)\s*,'
                          r'\s*([^,]+)\s*\)\s*$')
    for line in stdout_stream:
        match = POINT_RE.match(line)
        if match:
            x = float(match.group(1))
            y = float(match.group(2))
            z = float(match.group(3))
            yield (x, y, z)
        # Non-matching lines are discarded. AIMS tends to print messages,
        # warnings, etc. on stdout, so we are more robust by ignoring output
        # that we cannot parse.
