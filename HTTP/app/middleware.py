async def auth_middleware(request, call_next):
    api_key = request.headers.get("key")
    
    if api_key != "1234": 
        print("[AUTH] Missing or invalid API key")
        from core.response import Response
        response = Response()
        response.status = 401
        response.set_body("Unauthorized", "text/plain")
        return response

    print("[AUTH] Valid API key")
    return await call_next(request)


def setup_middleware(app):
    pass