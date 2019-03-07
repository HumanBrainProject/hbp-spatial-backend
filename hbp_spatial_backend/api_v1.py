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

import os.path

import flask
from flask import current_app, g, request, jsonify

from hbp_spatial_backend import apply_transform
from hbp_spatial_backend.transform_graph import TransformGraph


bp = flask.Blueprint('api_v1', __name__, url_prefix='/v1')


def get_transform_graph():
    if 'transform_graph' not in g:
        tg_path = current_app.config['DEFAULT_TRANSFORM_GRAPH']
        g.transform_graph_cwd = os.path.dirname(tg_path)
        with open(tg_path, 'rb') as f:
            g.transform_graph = TransformGraph.from_yaml(f)
    return g.transform_graph


@bp.route('/transform-point')
def transform_point():
    source_space = request.args['source_space']
    target_space = request.args['target_space']
    x = float(request.args['x'])
    y = float(request.args['y'])
    z = float(request.args['z'])
    source_point = (x, y, z)

    tg = get_transform_graph()
    transform_chain = tg.get_transform_chain(source_space, target_space)
    target_point = apply_transform.transform_point(
        source_point, transform_chain, cwd=g.transform_graph_cwd)

    return jsonify({'target_point': target_point})
