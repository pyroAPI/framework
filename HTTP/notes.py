# expmple web app
#run with: python -m waitress --listen=*:8000 notes:app       

from core.api import API
import json

app = API()

todos = {}
next_id = 1

@app.route('/todos', methods=['GET'])
def list_todos(request, response):
    response.content_type = 'application/json'
    response.text = json.dumps(list(todos.values()))

@app.route('/todos', methods=['POST'])
def create_todo(request, response):
    global next_id
    try:
        data = request.json_body
        todo = {
            'id': next_id,
            'title': data['title'],
            'done': False
        }
        todos[next_id] = todo
        next_id += 1
        response.status = 201
        response.content_type = 'application/json'
        response.text = json.dumps(todo)
    except Exception:
        response.status = 400
        response.text = 'Invalid JSON or missing "title"'

@app.route('/todos/{id}', methods=['GET'])
def get_todo(request, response, id):
    todo = todos.get(int(id))
    if not todo:
        response.status = 404
        response.text = 'Todo not found'
    else:
        response.content_type = 'application/json'
        response.text = json.dumps(todo)

