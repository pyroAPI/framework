"""
Example application showing how to use the router system
This replaces your main.py to demonstrate routing
"""
import asyncio
from router import Router
from server import handle_client
from http_objects import Request, Response
from middleware import logger_middleware, auth_middleware


# Create router instance
app = Router()

# In-memory data store for demo
users_db = [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
]

posts_db = [
    {"id": 1, "title": "Hello World", "content": "First post", "user_id": 1},
    {"id": 2, "title": "Python Tutorial", "content": "Learn Python", "user_id": 2}
]


# ===============================
# ROUTE DEFINITIONS
# ===============================

@app.get('/')
def home(request: Request):
    """Home page"""
    return Response.json({
        "message": "Welcome to your HTTP Framework!",
        "version": "1.0.0",
        "endpoints": [
            "GET /",
            "GET /users",
            "GET /users/{id}",
            "POST /users",
            "PUT /users/{id}",
            "DELETE /users/{id}",
            "GET /posts",
            "GET /posts/{id}",
            "GET /health"
        ]
    })


@app.get('/health')
def health_check(request: Request):
    """Health check endpoint"""
    return Response.json({
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    })


# ===============================
# USER ROUTES
# ===============================

@app.get('/users')
def get_users(request: Request):
    print(f"Dispatching: {request.method} {request.path}")
    """Get all users with optional filtering"""
    # Check for query parameters
    name_filter = request.get_query_param('name')
    
    filtered_users = users_db
    if name_filter:
        filtered_users = [u for u in users_db if name_filter.lower() in u['name'].lower()]
    
    return Response.json({
        "users": filtered_users,
        "count": len(filtered_users),
        "filters": {"name": name_filter} if name_filter else {}
    })


@app.get('/users/{id}')
def get_user(request: Request):
    """Get single user by ID"""
    user_id = int(request.route_params['id'])
    
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        return Response.error(f"User with id {user_id} not found", 404)
    
    return Response.json(user)


@app.post('/users')
def create_user(request: Request):
    """Create new user"""
    if not request.is_json():
        return Response.error("Content-Type must be application/json", 400)
    
    data = request.json()
    
    # Validate required fields
    if not data or 'name' not in data or 'email' not in data:
        return Response.error("Missing required fields: name, email", 400)
    
    # Create new user
    new_user = {
        "id": max([u['id'] for u in users_db]) + 1 if users_db else 1,
        "name": data['name'],
        "email": data['email']
    }
    
    users_db.append(new_user)
    
    return Response.json(new_user, status=201)


@app.put('/users/{id}')
def update_user(request: Request):
    """Update existing user"""
    user_id = int(request.route_params['id'])
    
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        return Response.error(f"User with id {user_id} not found", 404)
    
    if not request.is_json():
        return Response.error("Content-Type must be application/json", 400)
    
    data = request.json()
    
    # Update user fields
    if 'name' in data:
        user['name'] = data['name']
    if 'email' in data:
        user['email'] = data['email']
    
    return Response.json(user)


@app.delete('/users/{id}')
def delete_user(request: Request):
    """Delete user"""
    user_id = int(request.route_params['id'])
    
    user_index = next((i for i, u in enumerate(users_db) if u['id'] == user_id), None)
    if user_index is None:
        return Response.error(f"User with id {user_id} not found", 404)
    
    deleted_user = users_db.pop(user_index)
    
    return Response.json({
        "message": f"User {user_id} deleted successfully",
        "deleted_user": deleted_user
    })


# ===============================
# POST ROUTES
# ===============================

@app.get('/posts')
def get_posts(request: Request):
    """Get all posts with optional user filter"""
    user_id = request.get_query_param('user_id')
    
    filtered_posts = posts_db
    if user_id:
        filtered_posts = [p for p in posts_db if p['user_id'] == int(user_id)]
    
    return Response.json({
        "posts": filtered_posts,
        "count": len(filtered_posts)
    })


@app.get('/posts/{id}')
def get_post(request: Request):
    """Get single post by ID"""
    post_id = int(request.route_params['id'])
    
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        return Response.error(f"Post with id {post_id} not found", 404)
    
    return Response.json(post)


# ===============================
# ADVANCED ROUTES
# ===============================

@app.route('/api/search', methods=['GET', 'POST'])
def search(request: Request):
    """Search endpoint that accepts both GET and POST"""
    if request.method == 'GET':
        query = request.get_query_param('q', '')
    else:  # POST
        data = request.json() if request.is_json() else {}
        query = data.get('query', '')
    
    # Simple search in users and posts
    user_results = [u for u in users_db if query.lower() in u['name'].lower()]
    post_results = [p for p in posts_db if query.lower() in p['title'].lower()]
    
    return Response.json({
        "query": query,
        "results": {
            "users": user_results,
            "posts": post_results
        },
        "total": len(user_results) + len(post_results)
    })


@app.get('/users/{user_id}/posts')
def get_user_posts(request: Request):
    """Get posts by specific user"""
    user_id = int(request.route_params['user_id'])
    
    # Check if user exists
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        return Response.error(f"User with id {user_id} not found", 404)
    
    user_posts = [p for p in posts_db if p['user_id'] == user_id]
    
    return Response.json({
        "user": user,
        "posts": user_posts,
        "count": len(user_posts)
    })


