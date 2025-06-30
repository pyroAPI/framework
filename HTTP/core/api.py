


import asyncio
import traceback
from urllib.parse import parse_qs

from .request import Request
from .response import Response
from .utils import parse_headers, encode_headers


MAX_BODY_SIZE = 1024 * 1024


class API:
    def __init__(self):
        self.routes = {}        
        self._middlewares = []   
    def route(self, path, methods=None,middleware=None):
        def wrapper(handler):
            entry={
                "handler":handler,
                "middleware": middleware if isinstance(middleware, list) else [middleware] if middleware else []
            }
            if methods:
                self.routes.setdefault(path, {})
                for method in methods:
                    self.routes[path][method.upper()] = entry
            else:
                self.routes[path] = entry
            return handler
        return wrapper

    def add_middleware(self, middleware):
        self._middlewares.append(middleware)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return

        request = await self.build_request(scope, receive)
        response = await self.handle_request(request)
        await self.send_response(send, response)

    async def build_request(self, scope, receive):
        method = scope["method"].upper()
        path = scope["path"]
        headers = parse_headers(scope.get("headers", []))
        query_string = scope.get("query_string", b"").decode()
        query = parse_qs(query_string)

        body = b""
        if method in ("POST", "PUT", "PATCH"):
            while True:
                message = await receive()
                body += message.get("body", b"")
                if len(body) > MAX_BODY_SIZE:
                    raise Exception("Request body too large")
                if not message.get("more_body", False):
                    break
        else:
            await receive()

        return Request(method, path, headers, body, query)

    async def handle_request(self, request):
        from .router import find_handler  

        handler_entry, kwargs = find_handler(self.routes, request.path)
        if handler_entry is None:
            return Response(404, {"content-type": "text/plain"}, b"Not Found")

        # Get handler and route middleware
        if isinstance(handler_entry, dict):
            entry = handler_entry.get(request.method)
            if not entry:
                return Response(405, {"content-type": "text/plain"}, b"Method Not Allowed")
        else:
            entry = handler_entry

        # If the entry is a plain function then wrap it
        if callable(entry):
            handler = entry
            route_middlewares = []
        else:
            handler = entry["handler"]
            route_middlewares = entry.get("middleware", [])

        async def final_handler(req):
            response = Response()
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(req, response, **kwargs)
                else:
                    def run_sync():
                        handler(req, response, **kwargs)
                    await asyncio.to_thread(run_sync)
            except Exception:
                response.status = 500
                response.set_body("Internal Server Error")
                traceback.print_exc()
            return response

        # Apply route and global middleware 
        for mw in reversed(route_middlewares + self._middlewares):
            next_handler = final_handler
            async def final_handler_wrapped(req, mw=mw, nxt=next_handler):
                result = mw(req, nxt)
                if asyncio.iscoroutine(result):
                    return await result
                return result
            final_handler = final_handler_wrapped

        return await final_handler(request)


    async def send_response(self, send, response):
        await send({
            "type": "http.response.start",
            "status": response.status,
            "headers": encode_headers(response.headers),
        })
        await send({
            "type": "http.response.body",
            "body": response.body
        })
