from core.request import Request
from core.response import Response
from .model import db
from .middleware import auth_middleware

def setup_routes(app):
        
    # GET /users = list all
    @app.route("/users", methods=["GET"],)
    async def get_users(request: Request, response: Response):
        users = await db.all("User")
        response.set_json([u.__data__ for u in users])

    # GET /users?id=1 = single user
    @app.route("/users/find", methods=["GET"],middleware=auth_middleware)
    async def get_one_user(request: Request, response: Response):
        user_id = request.query.get("id", [None])[0]
        print(f"Looking for user ID: {user_id}")
        
        if not user_id:
            print("User ID missing")
            response.set_body("Missing id", "text/plain")
            response.status = 400
            return

        user = await db.get("User", id=int(user_id))
        print("User result:", user)

        if not user:
            print("User not found")
            response.set_body("Not Found", "text/plain")
            response.status = 404
            return

        print("User found:", user.__data__)
        response.set_json(user.__data__)

    # POST /users = create new user
    @app.route("/users", methods=["POST"])
    async def create_user(request: Request, response: Response):
        import json
        data = json.loads(request.body.decode())
        user = await db.create("User", name=data["name"], email=data["email"])
        response.set_json(user.__data__)
        response.status = 201

    # PATCH /users?id=1 = update name/email
    @app.route("/users", methods=["PATCH"])
    async def update_user(request: Request, response: Response):
        import json
        user_id = request.query.get("id", [None])[0]
        if not user_id:
            response.status = 400
            response.set_body("Missing id")
            return
        data = json.loads(request.body.decode())
        updated = await db.update("User", {"id": int(user_id)}, data)
        if updated:
            response.set_body("Updated")
        else:
            response.status = 404
            response.set_body("User not found")

    # DELETE /users?id=1
    @app.route("/users", methods=["DELETE"])
    async def delete_user(request: Request, response: Response):
        user_id = request.query.get("id", [None])[0]
        if not user_id:
            response.status = 400
            response.set_body("Missing id")
            return
        deleted = await db.delete("User", id=int(user_id))
        if deleted:
            response.set_body("Deleted")
        else:
            response.status = 404
            response.set_body("User not found")