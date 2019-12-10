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

"""Module containing a Flask application singleton for use by a WSGI server."""


import hbp_spatial_backend
application = hbp_spatial_backend.create_app()
