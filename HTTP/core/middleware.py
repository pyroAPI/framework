import asyncio
from .api import Request, Response

class MiddlewareManager:
    def __init__(self):
        self._middlewares = []

    def add(self, middleware):
        self._middlewares.append(middleware)

    def build(self, final_handler):
        handler = final_handler
        for middleware in reversed(self._middlewares):
            handler = self._wrap(handler, middleware)
        return handler

    def _wrap(self, handler, middleware):
        async def wrapped(request):
            result = middleware(request, handler)
            if asyncio.iscoroutine(result):
                result = await result
            return result
        return wrapped
