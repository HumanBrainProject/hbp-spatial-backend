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

import flask_restful
import flask_restful.reqparse

from hbp_spatial_backend import apply_transform


def tuple_3floats(input_sequence):
    '''Convert a variable to a tuple of 3 floats

    TypeError is raised if the conversion is not possible.
    '''
    input_tuple = tuple(input_sequence)
    if len(input_tuple) != 3:
        raise TypeError('the input sequence is not of length 3')
    return tuple(float(x) for x in input_tuple)


class TransformPointApi(flask_restful.Resource):
    def get(self):
        parser = flask_restful.reqparse.RequestParser()
        parser.add_argument('source_space', required=True, location='json')
        parser.add_argument('target_space', required=True, location='json')
        parser.add_argument('source_point', required=True,
                            type=tuple_3floats, location='json')
        args = parser.parse_args(strict=True)
        # transform_chain = transform_graph.get_chain(source_space,
        #                                             target_space)
        transform_chain = []
        target_point = apply_transform.transform_point(args.source_point,
                                                       transform_chain)
        target_point = args.source_point
        return {'target_point': target_point}


def register_api(app, *args, **kwargs):
    api = flask_restful.Api(app, *args, **kwargs)
    api.add_resource(TransformPointApi, '/transform-point')
