# Copyright 2019–2020 CEA
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

import logging
import os.path

import flask
from flask import current_app, g, jsonify
import flask_smorest
from flask_smorest import abort
import marshmallow
from marshmallow import Schema, fields
from marshmallow.validate import Length

from hbp_spatial_backend import apply_transform
from hbp_spatial_backend.transform_graph import TransformGraph


logger = logging.getLogger(__name__)

bp = flask_smorest.Blueprint(
    'api_v1', __name__, url_prefix='/v1',
    description='''\
First version of the API, which uses a static set of cross-space
transformations.

This service allows clients to transfer data between the core template brains
of the HBP. These are the four template spaces, along with their identifiers
which are used within this API:

- [MNI ICBM152 nonlinear 2009c asymmetric](http://nist.mni.mcgill.ca/?p=904)
  (`MNI 152 ICBM 2009c Nonlinear Asymmetric`);
- [MNI Colin27](http://nist.mni.mcgill.ca/?p=935) (`MNI Colin 27`);
- [BigBrain](https://doi.org/10.1126%2Fscience.1235381), 2015 release in
  histological space (`Big Brain (Histology)`);
- [Infant template](https://doi.org/10.25493%2F49QZ-AWZ) (`Infant Atlas`).
''',
)


def _get_transform_graph():
    if 'transform_graph' not in g:
        tg_path = current_app.config['DEFAULT_TRANSFORM_GRAPH']
        g.transform_graph_cwd = os.path.dirname(tg_path)
        with open(tg_path, 'rb') as f:
            g.transform_graph = TransformGraph.from_yaml(f)
    return g.transform_graph


@bp.route('/graph.yaml')
@bp.response()
def get_graph_yaml():
    """Download the graph.yaml file used by this API."""
    return flask.send_file(current_app.config['DEFAULT_TRANSFORM_GRAPH'],
                           mimetype='text/x-yaml')


class TransformPointRequestSchema(Schema):
    class Meta:
        ordered = True
    source_space = fields.Str(
        required=True,
        description='identifier of the source template space',
        example='MNI 152 ICBM 2009c Nonlinear Asymmetric',
    )
    target_space = fields.Str(
        required=True,
        description='identifier of the target template space',
        example='Big Brain (Histology)',
    )
    x = fields.Float(
        required=True,
        description='floating-point X coordinate of the source point',
        example=1.0,
    )
    y = fields.Float(
        required=True,
        description='floating-point Y coordinate of the source point',
        example=2.0
    )
    z = fields.Float(
        required=True,
        description='floating-point Z coordinate of the source point',
        example=3.0,
    )


class TransformPointResponseSchema(Schema):
    target_point = fields.List(
        fields.Float, validate=Length(equal=3), required=True,
    )


class ErrorResponseSchema(Schema):
    class Meta:
        unknown = marshmallow.INCLUDE
        strict = False
    code = fields.Integer(required=False)
    status = fields.String(required=False)
    message = fields.String(required=False)
    errors = fields.Dict(keys=fields.String(), required=False)


@bp.route('/transform-point')
@bp.arguments(TransformPointRequestSchema, location='query')
# The error responses come first, the schemas are only used for
# documentation
@bp.response(ErrorResponseSchema,
             code=400,
             example={'message': 'source_space or target_space not found'})
# Code 422 is raised by webargs for request validation errors
@bp.response(ErrorResponseSchema,
             code=422, description='Semantically invalid request')
# The successful response must be the last response decorator, its schema
# is used for serializing the response.
@bp.response(TransformPointResponseSchema,
             example={
                 'target_point': [2.20432, 14.2799, -2.02697],
             })
def transform_point(args):
    """Transform a single point."""
    source_point = (args['x'], args['y'], args['z'])
    source_space = args['source_space']
    target_space = args['target_space']

    tg = _get_transform_graph()
    try:
        transform_chain = tg.get_transform_chain(source_space, target_space)
    except KeyError:
        abort(400, message='source_space or target_space not found')
    target_point = apply_transform.transform_point(
        source_point, transform_chain, cwd=g.transform_graph_cwd)

    response = jsonify(TransformPointResponseSchema().dump({
        'target_point': target_point,
    }))
    response.cache_control.public = True
    response.cache_control.max_age = 86400  # 1 day
    return response


class TransformPointsRequestSchema(Schema):
    class Meta:
        ordered = True
    source_space = fields.Str(
        required=True,
        description='identifier of the source template space',
    )
    target_space = fields.Str(
        required=True,
        description='identifier of the target template space',
    )
    source_points = fields.List(
        fields.List(fields.Float, validate=Length(equal=3)),
        required=True,
        description='list of points to be transformed, each point is a '
                    '[x, y, z] triple of coordinates',
    )


class TransformPointsResponseSchema(Schema):
    target_points = fields.List(
        fields.List(fields.Float, validate=Length(equal=3)),
        required=True,
    )


@bp.route('/transform-points', methods=['POST'])
@bp.arguments(TransformPointsRequestSchema, location='json',
              example={
                  'source_space': 'MNI 152 ICBM 2009c Nonlinear Asymmetric',
                  'target_space': 'Big Brain (Histology)',
                  'source_points': [
                      [1, 2, 3],
                      [50.2, 10.1, -40.8],
                  ],
              })
# The error responses come first, the schemas are only used for
# documentation
@bp.response(ErrorResponseSchema,
             code=400,
             example={'message': 'source_space or target_space not found'})
# Code 422 is raised by webargs for request validation errors
@bp.response(ErrorResponseSchema,
             code=422, description='Semantically invalid request')
# The successful response must be the last response decorator, its schema
# is used for serializing the response.
@bp.response(TransformPointsResponseSchema,
             example={
                 'target_points': [
                     [2.20432, 14.2799, -2.02697],
                     [55.8957, 16.8771, -25.3469],
                 ],
             })
def transform_points(args):
    """Transform a batch of points."""
    source_space = args['source_space']
    target_space = args['target_space']

    tg = _get_transform_graph()
    try:
        transform_chain = tg.get_transform_chain(source_space, target_space)
    except KeyError:
        abort(400, errors=['source_space or target_space not found'])
    target_points = apply_transform.transform_points(
        args['source_points'], transform_chain, cwd=g.transform_graph_cwd)

    return {'target_points': target_points}
