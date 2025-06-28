import re
import asyncio
from typing import Dict, List, Callable, Optional, Tuple
from http_objects import Request, Response


class Route:
    def __init__(self, method: str, pattern: str, handler: Callable, name: str = None):
        self.method = method.upper()
        self.pattern = pattern
        self.handler = handler
        self.name = name or f"{method}_{pattern}"
        self.regex, self.param_names = self._compile_pattern(pattern)

    def _compile_pattern(self, pattern: str) -> Tuple[re.Pattern, List[str]]:
        param_names = []
        param_pattern = r'\{([^}]+)\}'
        params = re.findall(param_pattern, pattern)
        param_names.extend(params)

        regex_pattern = pattern
        for param in params:
            regex_pattern = regex_pattern.replace(f'{{{param}}}', f'(?P<{param}>[^/]+)')
        regex_pattern = f'^{regex_pattern}$'

        return re.compile(regex_pattern), param_names

    def match(self, method: str, path: str) -> Optional[Dict[str, str]]:
        if self.method != method.upper():
            return None
        match = self.regex.match(path)
        if match:
            return match.groupdict()
        return None


class Router:
    def __init__(self):
        self.routes: List[Route] = []
        self.middleware: List[Callable] = []

    def add_route(self, method: str, pattern: str, handler: Callable, name: str = None):
        route = Route(method, pattern, handler, name)
        self.routes.append(route)
        return route

    def get(self, pattern: str, name: str = None):
        def decorator(handler):
            self.add_route('GET', pattern, handler, name)
            return handler
        return decorator

    def post(self, pattern: str, name: str = None):
        def decorator(handler):
            self.add_route('POST', pattern, handler, name)
            return handler
        return decorator

    def put(self, pattern: str, name: str = None):
        def decorator(handler):
            self.add_route('PUT', pattern, handler, name)
            return handler
        return decorator

    def delete(self, pattern: str, name: str = None):
        def decorator(handler):
            self.add_route('DELETE', pattern, handler, name)
            return handler
        return decorator

    def route(self, pattern: str, methods: List[str] = None, name: str = None):
        if methods is None:
            methods = ['GET']
        def decorator(handler):
            for method in methods:
                self.add_route(method, pattern, handler, name)
            return handler
        return decorator

    def add_middleware(self, middleware: Callable):
        self.middleware.append(middleware)

    def match(self, method: str, path: str) -> Optional[Tuple[Route, Dict[str, str]]]:
        for route in self.routes:
            params = route.match(method, path)
            if params is not None:
                return route, params
        return None

    async def dispatch(self, request: Request) -> Response:
        # Apply middleware
        for middleware in self.middleware:
            try:
                result = await self._call_middleware(middleware, request)
                if isinstance(result, Response):
                    return result  # short-circuited (e.g. 401 Unauthorized)
                request = result
            except Exception as e:
                return Response.error(f"Middleware error: {str(e)}", 500)

        match_result = self.match(request.method, request.path)
        if match_result is None:
            return self._handle_404(request)

        route, params = match_result
        request.route_params = params

        try:
            if self._is_async_function(route.handler):
                response = await route.handler(request)
            else:
                response = route.handler(request)

            if not isinstance(response, Response):
                if isinstance(response, dict):
                    response = Response.json(response)
                elif isinstance(response, str):
                    response = Response(response)
                else:
                    response = Response(str(response))

            return response

        except Exception as e:
            print(f"Handler error: {e}")
            return Response.error(f"Internal server error: {str(e)}", 500)

    def _is_async_function(self, func):
        return asyncio.iscoroutinefunction(func)

    async def _call_middleware(self, middleware, request):
        if self._is_async_function(middleware):
            return await middleware(request)
        else:
            return middleware(request)

    def _handle_404(self, request: Request) -> Response:
        return Response.error(f"Route not found: {request.method} {request.path}", 404)

    def list_routes(self):
        return [
            {
                'method': route.method,
                'pattern': route.pattern,
                'name': route.name,
                'handler': route.handler.__name__
            }
            for route in self.routes
        ]

    def url_for(self, name: str, **params) -> str:
        for route in self.routes:
            if route.name == name:
                url = route.pattern
                for param_name, param_value in params.items():
                    url = url.replace(f'{{{param_name}}}', str(param_value))
                return url
        raise ValueError(f"Route with name '{name}' not found")


# Global instance
default_router = Router()

def create_router() -> Router:
    return Router()
