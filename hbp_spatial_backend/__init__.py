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

import os

import flask


# __version__ and SOURCE_URL are used by setup.py and docs/conf.py (they are
# parsed with a regular expression, so keep the syntax simple).
__version__ = '0.1.0.dev0'

# URL that holds the source code of the backend. This must be changed to
# point to the exact code of any modified version, in order to comply with
# the AGPL licence.
SOURCE_URL = 'https://github.com/HumanBrainProject/hbp-spatial-backend'


class DefaultConfig:
    CORS_ALLOW_ALL = True


# This function has a magic name which is recognized by flask as a factory for
# the main app.
def create_app(test_config=None):
    app = flask.Flask(__name__,
                      instance_path=os.environ.get("INSTANCE_PATH"),
                      instance_relative_config=True)

    app.config.from_object(DefaultConfig)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
        app.config.from_envvar("HBP_SPATIAL_BACKEND_SETTINGS", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if app.config["CORS_ALLOW_ALL"]:
        import flask_cors
        flask_cors.CORS(app)

    @app.route("/source")
    def root():
        return flask.redirect(SOURCE_URL)

    import hbp_spatial_backend.api_v1
    hbp_spatial_backend.api_v1.register_api(app, prefix='/v1')

    return app
