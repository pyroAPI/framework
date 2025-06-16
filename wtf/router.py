import re
from typing import Dict, List, Callable, Optional, Tuple
from http_objects import Request, Response


class Route:
    """Represents a single route with method, pattern, and handler"""
    def __init__(self, method: str, pattern: str, handler: Callable, name: str = None):
        self.method = method.upper()
        self.pattern = pattern
        self.handler = handler
        self.name = name or f"{method}_{pattern}"
        
        # Convert URL pattern to regex
        self.regex, self.param_names = self._compile_pattern(pattern)
    
    def _compile_pattern(self, pattern: str) -> Tuple[re.Pattern, List[str]]:
        """Convert URL pattern like /users/{id} to regex and extract parameter names"""
        param_names = []
        
        # Find all parameters in curly braces like {id}, {name}
        param_pattern = r'\{([^}]+)\}'
        params = re.findall(param_pattern, pattern)
        param_names.extend(params)
        
        # Replace {param} with regex groups
        regex_pattern = pattern
        for param in params:
            # Replace {param} with named group that matches anything except /
            regex_pattern = regex_pattern.replace(f'{{{param}}}', f'(?P<{param}>[^/]+)')
        
        # Add start and end anchors
        regex_pattern = f'^{regex_pattern}$'
        
        return re.compile(regex_pattern), param_names
    
    def match(self, method: str, path: str) -> Optional[Dict[str, str]]:
        """Check if this route matches the request method and path"""
        if self.method != method.upper():
            return None
        
        match = self.regex.match(path)
        if match:
            return match.groupdict()
        return None


class Router:
    """Main router class that manages all routes"""
    def __init__(self):
        self.routes: List[Route] = []
        self.middleware: List[Callable] = []
    
    def add_route(self, method: str, pattern: str, handler: Callable, name: str = None):
        """Add a single route"""
        route = Route(method, pattern, handler, name)
        self.routes.append(route)
        return route
    
    def get(self, pattern: str, name: str = None):
        """Decorator for GET routes"""
        def decorator(handler):
            self.add_route('GET', pattern, handler, name)
            return handler
        return decorator
    
    def post(self, pattern: str, name: str = None):
        """Decorator for POST routes"""
        def decorator(handler):
            self.add_route('POST', pattern, handler, name)
            return handler
        return decorator
    
    def put(self, pattern: str, name: str = None):
        """Decorator for PUT routes"""
        def decorator(handler):
            self.add_route('PUT', pattern, handler, name)
            return handler
        return decorator
    
    def delete(self, pattern: str, name: str = None):
        """Decorator for DELETE routes"""
        def decorator(handler):
            self.add_route('DELETE', pattern, handler, name)
            return handler
        return decorator
    
    def route(self, pattern: str, methods: List[str] = None, name: str = None):
        """Decorator for multiple methods on same route"""
        if methods is None:
            methods = ['GET']
        
        def decorator(handler):
            for method in methods:
                self.add_route(method, pattern, handler, name)
            return handler
        return decorator
    
    def add_middleware(self, middleware: Callable):
        """Add middleware function"""
        self.middleware.append(middleware)
    
    def match(self, method: str, path: str) -> Optional[Tuple[Route, Dict[str, str]]]:
        """Find matching route for method and path"""
        for route in self.routes:
            params = route.match(method, path)
            if params is not None:
                return route, params
        return None
    
    async def dispatch(self, request: Request) -> Response:
        """Main dispatch method - finds route and calls handler"""
        # Apply middleware to request
        for middleware in self.middleware:
            try:
                request = await self._call_middleware(middleware, request)
            except Exception as e:
                return Response.error(f"Middleware error: {str(e)}", 500)
        
        # Find matching route
        match_result = self.match(request.method, request.path)
        
        if match_result is None:
            return self._handle_404(request)
        
        route, params = match_result
        
        # Add route parameters to request object
        request.route_params = params
        
        try:
            # Call the handler
            if self._is_async_function(route.handler):
                response = await route.handler(request)
            else:
                response = route.handler(request)
            
            # Ensure response is a Response object
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
        """Check if function is async"""
        import asyncio
        return asyncio.iscoroutinefunction(func)
    
    async def _call_middleware(self, middleware, request):
        """Call middleware function (sync or async)"""
        if self._is_async_function(middleware):
            return await middleware(request)
        else:
            return middleware(request)
    
    def _handle_404(self, request: Request) -> Response:
        """Handle 404 errors"""
        return Response.error(f"Route not found: {request.method} {request.path}", 404)
    
    def list_routes(self):
        """List all registered routes (for debugging)"""
        routes_info = []
        for route in self.routes:
            routes_info.append({
                'method': route.method,
                'pattern': route.pattern,
                'name': route.name,
                'handler': route.handler.__name__
            })
        return routes_info
    
    def url_for(self, name: str, **params) -> str:
        """Generate URL for a named route with parameters"""
        for route in self.routes:
            if route.name == name:
                url = route.pattern
                for param_name, param_value in params.items():
                    url = url.replace(f'{{{param_name}}}', str(param_value))
                return url
        raise ValueError(f"Route with name '{name}' not found")


# Convenience function to create a router instance
def create_router() -> Router:
    """Create a new router instance"""
    return Router()


# Global router instance (optional - for simple apps)
default_router = Router()