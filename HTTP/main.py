from core.api import API
from app.routes import setup_routes
from app.middleware import setup_middleware

app = API()
setup_middleware(app)
setup_routes(app)


