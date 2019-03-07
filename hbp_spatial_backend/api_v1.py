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
from flask import current_app, g, jsonify, request

import marshmallow
from marshmallow import Schema, fields

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


class TransformPointRequestSchema(Schema):
    source_space = fields.Str(required=True)
    target_space = fields.Str(required=True)
    x = fields.Float(required=True)
    y = fields.Float(required=True)
    z = fields.Float(required=True)


@bp.route('/transform-point')
def transform_point():
    args = TransformPointRequestSchema().load(request.args)
    source_point = (args['x'], args['y'], args['z'])
    source_space = args['source_space']
    target_space = args['target_space']

    tg = get_transform_graph()
    try:
        transform_chain = tg.get_transform_chain(source_space, target_space)
    except KeyError:
        return jsonify(
            {'errors': ['source_space or target_space not found']}
        ), 400
    target_point = apply_transform.transform_point(
        source_point, transform_chain, cwd=g.transform_graph_cwd)

    return jsonify({'target_point': target_point})


@bp.errorhandler(marshmallow.exceptions.ValidationError)
def handle_validation_error(exc):
    return jsonify({'errors': exc.messages}), 400
