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

import re
import subprocess


POINT_RE = re.compile(r'\(\s*([^,]*)\s*,\s*([^,]*)\s*,\s*([^,]*)\s*\)')


def transform_point(source_point, direct_transform_chain, cwd=None):
    transform_params = []
    for t in direct_transform_chain:
        transform_params.extend(['--direct-transform', t])
    res = subprocess.run(
        ['AimsApplyTransform',
         '--points',
         '--mmap-fields',
         '--input', '-',
         '--output', '-'] + transform_params,
        check=True,
        input='({0}, {1}, {2})'.format(*source_point),
        stdout=subprocess.PIPE, universal_newlines=True,
        cwd=cwd)
    match = POINT_RE.search(res.stdout)
    if not match:
        raise RuntimeError('Cannot parse output of AimsApplyTransform')
    x = float(match.group(1))
    y = float(match.group(2))
    z = float(match.group(3))
    return (x, y, z)
