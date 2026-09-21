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
import shlex
import subprocess
import time

from flask import current_app
from soma import aims, aimsalgo


logger = logging.getLogger(__name__)

graph = {}


def load_graph(graph_file):
    global graph
    if graph_file in graph:
        return graph[graph_file]
    g = aims.read(graph_file)
    # set fields allocator for mmap preferably
    ac = aims.carto.AllocatorContext(aims.carto.AllocatorStrategy.ReadOnly)
    ac.setUseFactor(0.)
    g.setAllocatorContext(ac)

    graph[graph_file] = g

    return g


def transform_points(source_points, input_space, output_space, graph,
                     cwd=None):
    time_before = time.perf_counter()

    gr = load_graph(graph)
    edge = gr.getTransformation(input_space, output_space, True)
    if edge is None:
        return None
    tr = gr.transformation(edge).get()

    target_points = [tr.transform(p) for p in source_points]

    elapsed_time = time.perf_counter() - time_before
    logger.info('Transform completed in %.3f s', elapsed_time)
    assert len(target_points) == len(source_points)
    return target_points


def get_transform_command(input_space,
                          graph,
                          output_space=None,
                          output_coords=None,
                          reference=None,):
    cmd = ['AimsApplyTransform',
           '-g', graph,
           '--input-coords', input_space]
    if output_space:
        cmd += ['--output-space', output_space]
    if output_coords:
        cmd += ['--output-coords', output_coords]
    if reference:
        cmd.extend(['--reference', reference])
    return cmd


def transform_point(source_point, input_space, output_space, graph, cwd=None):
    target_points = transform_points([source_point],
                                     input_space, output_space, graph,
                                     cwd=cwd)
    assert len(target_points) == 1
    return target_points[0]


