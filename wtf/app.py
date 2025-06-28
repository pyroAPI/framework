# app.py

from router import Router
from http_objects import Response

# Create a router instance (like FastAPI/Flask's app)
app = Router()

# Example endpoint
def json_now():
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"

@app.get("/")
async def root(request):
    return Response.json({"message": "Welcome to your framework!"})

@app.get("/health")
async def health_check(request):
    return Response.json({
        "status": "healthy",
        "timestamp": json_now()
    })

@app.get("/users/{id}")
async def get_user(request):
    user_id = request.route_params.get("id")
    return Response.json({"user_id": user_id})
