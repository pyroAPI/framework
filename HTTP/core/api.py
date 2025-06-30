from webob import Request, Response
from .router import find_handler


class API:

    def __init__(self):
        self.routes = {}

    def route(self, path, methods=None):
        def wrapper(handler):
            if methods:
                if path not in self.routes:
                    self.routes[path] = {}
                elif not isinstance(self.routes[path], dict):
                    raise AssertionError(f'Route "{path}" already exists without methods.')

                for method in methods:
                    if method in self.routes[path]:
                        raise AssertionError(f'Method {method} already registered for route "{path}"')
                    self.routes[path][method] = handler
            else:
                if path in self.routes:
                    raise AssertionError(f'Route "{path}" already exists.')
                self.routes[path] = handler
            return handler
        return wrapper

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request):
        path = request.path
        method = request.method
        response = Response()

        handler_entry, kwargs = find_handler(self.routes, path)

        if handler_entry is None:
            response.status_code = 404
            response.body = b'Not Found'
            return response

        if isinstance(handler_entry, dict):
            handler = handler_entry.get(method)
            if not handler:
                response.status_code = 405
                response.body = b'Method Not Allowed'
                return response
        else:
            handler = handler_entry

        handler(request, response, **kwargs)
        return response

    def default_response(self, response):
        response.status = 404
        response.text = 'Not found'
