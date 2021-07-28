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
    """Download the graph.yaml file used by this API.

    The backend internally uses a YAML file to store the transformation graph
    which links the template spaces. **The format of this file is subject to
    change, this endpoint may be modified or removed at any time.**
    """
    logger.info('default path to graph.yaml: %s',
                current_app.config['DEFAULT_TRANSFORM_GRAPH'])
    logger.info('instance path: %s', current_app.instance_path)
    return flask.send_file(current_app.config['DEFAULT_TRANSFORM_GRAPH'],
                           mimetype='text/x-yaml')


class TransformPointRequestSchema(Schema):
    class Meta:
        ordered = True

    source_space = fields.Str(
        required=True,
        description='Identifier of the source template space.',
        example='MNI 152 ICBM 2009c Nonlinear Asymmetric',
    )
    target_space = fields.Str(
        required=True,
        description='Identifier of the target template space.',
        example='Big Brain (Histology)',
    )
    x = fields.Float(
        required=True,
        description='X coordinate of the source point, in millimetres.',
        example=1.0,
    )
    y = fields.Float(
        required=True,
        description='Y coordinate of the source point, in millimetres.',
        example=2.0
    )
    z = fields.Float(
        required=True,
        description='Z coordinate of the source point, in millimetres.',
        example=3.0,
    )


class TransformPointResponseSchema(Schema):
    target_point = fields.List(
        fields.Float, validate=Length(equal=3), required=True,
        description='Coordinates of the transformed point in the target '
                    'space, expressed as [x, y, z], in millimetres.',
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
        description='Identifier of the source template space.',
    )
    target_space = fields.Str(
        required=True,
        description='Identifier of the target template space.',
    )
    source_points = fields.List(
        fields.List(fields.Float, validate=Length(equal=3)),
        required=True,
        description='List of points to be transformed. Each point is a '
                    '[x, y, z] triple of coordinates in millimetres.',
    )


class TransformPointsResponseSchema(Schema):
    target_points = fields.List(
        fields.List(fields.Float, validate=Length(equal=3)),
        required=True,
        description='Coordinates of the transformed points in the target '
                    'space, in the same order as `source_points` in the '
                    'request. Each point is returned as a [x, y, z] triple '
                    'of coordinates in millimetres',
    )


class GetTransformCommandRequestSchema(Schema):
    class Meta:
        ordered = True

    source_space = fields.Str(
        required=True,
        description='Identifier of the source template space.',
        example='MNI 152 ICBM 2009c Nonlinear Asymmetric',
    )
    target_space = fields.Str(
        required=True,
        description='Identifier of the target template space.',
        example='MNI Colin 27',
    )
    input_coords = fields.Str(
        required=False,
        description="How to interpret coordinates in the input image w.r.t. "
                    "the transformations written in the image header. See "
                    "AimsApplyTransform --help for the list of supported "
                    "values.",
        load_default='auto',
        example='auto',
    )


class GetTransformCommandResponseSchema(Schema):
    transform_command = fields.List(
        fields.Str(),
        required=True,
        description='AimsApplyTransform command to use for transforming data '
                    'from source space to target space, given as a list of '
                    'commandline arguments',
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


@bp.route('/get-mesh-transform-command')
@bp.arguments(GetTransformCommandRequestSchema, location='query')
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
@bp.response(GetTransformCommandResponseSchema,
             example={
                 'transform_command': ["AimsApplyTransform", "--help"],
             })
def get_mesh_transform_command(args):
    """Get the transform command."""
    source_space = args['source_space']
    target_space = args['target_space']
    input_coords = args['input_coords']

    tg = _get_transform_graph()
    try:
        direct_transform_chain = tg.get_transform_chain(source_space,
                                                        target_space)
        inverse_transform_chain = tg.get_transform_chain(target_space,
                                                         source_space)
    except KeyError:
        abort(400, errors=['source_space or target_space not found'])

    transform_command = apply_transform.get_transform_command(
        direct_transform_chain=direct_transform_chain,
        inverse_transform_chain=inverse_transform_chain,
        input_coords=input_coords,
    )

    response = jsonify(GetTransformCommandResponseSchema().dump({
        'transform_command': transform_command,
    }))

    response.cache_control.public = True
    response.cache_control.max_age = 86400  # 1 day
    return response


@bp.route('/get-image-transform-command')
@bp.arguments(GetTransformCommandRequestSchema, location='query')
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
@bp.response(GetTransformCommandResponseSchema,
             example={
                 'transform_command': ["AimsApplyTransform", "--help"],
             })
def get_image_transform_command(args):
    """Get the transform command."""
    source_space = args['source_space']
    target_space = args['target_space']
    input_coords = args['input_coords']

    tg = _get_transform_graph()
    try:
        inverse_transform_chain = tg.get_transform_chain(target_space,
                                                         source_space)
    except KeyError:
        abort(400, errors=['source_space or target_space not found'])

    # For resampling images we have use AIMS image coordinates (whose origin is
    # in the corner of the field of view), so we have to remove the last affine
    # transformation of the chain, whose purpose is to go from these image
    # coordinates to template coordinates (whose origin is usually centered
    # around the center of the brain in the region of the anterior commissure).
    #
    # FIXME: This is a kind of hack that is specific to the way that the
    # transform graph is stored as of now. The proper solution will need
    # options to be added to AimsApplyTransform for properly specifying the
    # output geometry (i.e. setting the FoV).
    inverse_transform_chain = inverse_transform_chain[1:]
    reference = inverse_transform_chain[0]
    assert not reference.startswith('inv:')
    assert not reference.endswith('.trm')

    transform_command = apply_transform.get_transform_command(
        inverse_transform_chain=inverse_transform_chain,
        reference=reference,
        input_coords=input_coords,
    )

    response = jsonify(GetTransformCommandResponseSchema().dump({
        'transform_command': transform_command,
    }))

    response.cache_control.public = True
    response.cache_control.max_age = 86400  # 1 day
    return response
