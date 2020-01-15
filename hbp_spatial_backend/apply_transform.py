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
    if logger.isEnabledFor(logging.DEBUG):
        import shlex
        logger.debug('Transforming %d points with: %s', len(source_points),
                     ' '.join(shlex.quote(arg) for arg in cmd))
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
