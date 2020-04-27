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


def test_config():
    from hbp_spatial_backend import create_app
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_wsgi_app():
    from hbp_spatial_backend.wsgi import application
    assert application is not None


def test_root_route(client):
    response = client.get('/')
    assert response.status_code == 302


def test_source_route(client):
    response = client.get('/source')
    assert response.status_code == 302


def test_health_route(client):
    response = client.get('/health')
    assert response.status_code == 200


def test_echo_route():
    from hbp_spatial_backend import create_app
    app = create_app({'TESTING': True, 'ENABLE_ECHO': False})
    with app.test_client() as client:
        response = client.get('/echo')
    assert response.status_code == 404

    app = create_app({'TESTING': True, 'ENABLE_ECHO': True})
    with app.test_client() as client:
        response = client.get('/echo')
    assert response.status_code == 200


def test_CORS():
    from hbp_spatial_backend import create_app
    app = create_app({'TESTING': True, 'CORS_ORIGINS': None})
    with app.test_client() as client:
        response = client.get('/')
    assert 'Access-Control-Allow-Origin' not in response.headers
    app = create_app({'TESTING': True, 'CORS_ORIGINS': '*'})
    with app.test_client() as client:
        response = client.get('/')
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == '*'


def test_proxy_fix(caplog):
    from hbp_spatial_backend import create_app
    caplog.set_level(logging.INFO)

    app = create_app({
        'TESTING': True,
        'ENABLE_ECHO': True,
        'PROXY_FIX': None,
    })
    with app.test_client() as client:
        client.get('/echo', headers={'X-Forwarded-Host': 'h.test'})
    assert 'X-Forwarded-Host: h.test' in caplog.text
    assert 'Host: localhost' in caplog.text

    app = create_app(test_config={
        'TESTING': True,
        'PROXY_FIX': {
            'x_for': 1,
            'x_proto': 1,
            'x_host': 1,
            'x_port': 1,
            'x_prefix': 1,
        },
    })
    called = False

    @app.route('/test')
    def test():
        nonlocal called
        from flask import request
        assert request.url == 'https://h.test:1234/toto/test'
        assert request.access_route[0] == '1.2.3.4'
        called = True
        return ''

    client = app.test_client()
    client.get('/test', headers={
        'X-Forwarded-For': '1.2.3.4',
        'X-Forwarded-Proto': 'https',
        'X-Forwarded-Host': 'h.test',
        'X-Forwarded-Port': '1234',
        'X-Forwarded-Prefix': '/toto',
    })
    assert called


def test_openapi_spec(app, client):
    response = client.get('/openapi.json')
    assert response.status_code == 200
    assert response.json['openapi'] == app.config['OPENAPI_VERSION']
    assert 'info' in response.json
    assert 'title' in response.json['info']
    assert 'version' in response.json['info']
    assert 'license' in response.json['info']
    assert 'servers' in response.json
    for server_info in response.json['servers']:
        assert server_info['url'] != '/'


def test_openapi_spec_development_mode():
    from hbp_spatial_backend import create_app
    app = create_app({'TESTING': True, 'ENV': 'development'})
    with app.test_client() as client:
        response = client.get('/openapi.json')
    assert response.json['servers'][0]['url'] == '/'
