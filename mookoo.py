# -*- coding: utf-8 -*-

import os
import json
import argparse
from . import bottle

root_dir = None


def _to_json(val):
    return json.dumps(val, ensure_ascii=True, sort_keys=True)


def _remove_keys_copy(d, *keys):
    d1 = d.copy()
    for k in keys:
        try:
            del d1[k]
        except KeyError:
            pass
    return d1


def load_text(filename):
    with open(os.path.join(root_dir, filename)) as f:
        return f.read()


def load_json(filename):
    _, ext = os.path.splitext(filename)
    if ext == '.py':
        l = {}
        exec (load_text(filename), {'request': bottle.request}, l)
        return _to_json(l.get('JSON', None))
    else:
        return load_text(filename)


def static_file(filename, download=False):
    download_filename = False
    if download:
        download_filename = os.path.basename(filename) if download is True else download
    return bottle.static_file(filename, root_dir, download=download_filename)


class Cookie(object):
    def __init__(self, name, val, secret=None, **options):
        self.name, self.value, self.secret, self.options = name, val, secret, options

    @staticmethod
    def as_list(cookie_or_cookies):
        return [cookie_or_cookies] if isinstance(cookie_or_cookies, Cookie) else list(cookie_or_cookies)


class Response(object):
    def __init__(self, body, status=200, header=None, content_type=None, cookie=None):
        self.body = body
        self.status, self.header, self.content_type, self.cookie = status, header, content_type, cookie

    def gen_body(self):
        bottle.response.status = self.status
        if self.header:
            for k, v in self.header.items():
                bottle.response.set_header(k, str(v))
        if self.content_type:
            bottle.response.content_type = self.content_type
        if self.cookie:
            for cookie in Cookie.as_list(self.cookie):
                bottle.response.set_cookie(cookie.name, cookie.value, secret=cookie.secret, **cookie.options)
        return self.body() if callable(self.body) else self.body


class Route(object):
    def __init__(self, method, path):
        self._method, self._path = method, path
        self._response = None

    def handle(self, *args, **kwargs):
        if self._response is not None:
            return self._response.gen_body()
        else:
            bottle.response.status = 500
            bottle.response.content_type = 'text/plain'
            return 'Missing response'

    def _setup_route(self, fn):
        if self._method == 'ANY':
            return bottle.route(self._path)(fn)
        else:
            return bottle.route(self._path, self._method, fn)

    def __call__(self, fn):
        return self._setup_route(fn)

    # Response
    def response(self, *args, **kwargs):
        self._setup_route(self.handle)
        self._response = Response(*args, **kwargs)
        return self

    # Redirect
    def redirect(self, url):
        return self.response(url, status=302, header={'Location': url})

    # Static file
    def static_file(self, filename, download=False, **kwargs):
        return self.response(lambda: static_file(filename, download=download), **kwargs)

    # Content
    def _make_content_resp(self, val, content_type, **kwargs):
        return self.response(val, content_type=content_type, **_remove_keys_copy(kwargs, 'content_type'))

    def text(self, val, **kwargs):
        return self._make_content_resp(val, 'text/plain', **kwargs)

    def html(self, val, **kwargs):
        return self._make_content_resp(val, 'text/html', **kwargs)

    def js(self, val, **kwargs):
        return self._make_content_resp(val, 'text/javascript', **kwargs)

    def json(self, val, **kwargs):
        return self._make_content_resp(_to_json(val), 'application/json', **kwargs)

    def load_text(self, filename, **kwargs):
        return self._make_content_resp(lambda: load_text(filename), 'text/plain', **kwargs)

    def load_html(self, filename, **kwargs):
        return self._make_content_resp(lambda: load_text(filename), 'text/html', **kwargs)

    def load_js(self, filename, **kwargs):
        return self._make_content_resp(lambda: load_text(filename), 'text/javascript', **kwargs)

    def load_json(self, filename, **kwargs):
        return self._make_content_resp(lambda: load_json(filename), 'application/json', **kwargs)


def route(method, path):
    return Route(method, path)


def _make_route(method):
    return lambda path: route(method, path)


ANY = _make_route('ANY')
GET = _make_route('GET')
POST = _make_route('POST')
PUT = _make_route('PUT')
DELETE = _make_route('DELETE')
OPTIONS = _make_route('OPTIONS')
HEAD = _make_route('HEAD')


def run(port=None, root=None):
    global root_dir

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help="Port")
    parser.add_argument('-d', '--dir', help="Content directory")
    args = parser.parse_args()
    port = port or args.port or 7928
    root_dir = root or args.dir or os.getcwd()
    GET('/+mookoo').load_html('help.html')
    bottle.run(port=port, debug=True, reloader=True)