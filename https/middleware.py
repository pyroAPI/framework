import time
import logging
import jwt  # pip install PyJWT
from http_objects import Response

# ---------------------------------------
# Middleware Manager
# ---------------------------------------

class MiddlewareManager:
    def __init__(self):
        self.middlewares = []
    
    def add(self, middleware):
        self.middlewares.append(middleware)
    
    async def process_request(self, request):
        for middleware in self.middlewares:
            request = await middleware(request)
        return request

# ---------------------------------------
# Logging Middleware
# ---------------------------------------

# Set up logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def logger_middleware(request):
    start = time.time()
    method = request.method
    path = request.path
    ip = request.headers.get("X-Forwarded-For", "Unknown")

    logging.info(f"📥 Received {method} {path} from {ip}")

    if method in ["POST", "PUT"]:
        try:
            logging.debug(f"Payload: {request.body.decode(errors='ignore')}")
        except Exception:
            pass  # Don't let decoding errors break logs

    request._start_time = start
    return request

# ---------------------------------------
# Auth Middleware
# ---------------------------------------

SECRET_KEY = "your_super_secret_key"

async def auth_middleware(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return Response.error("Missing or invalid Authorization header", 401)

    token = auth_header.split(" ")[1]

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request.user = decoded
        return request
    except jwt.ExpiredSignatureError:
        return Response.error("Token expired", 401)
    except jwt.InvalidTokenError:
        return Response.error("Invalid token", 401)
