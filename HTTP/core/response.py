import json

class Response:
    def __init__(self, status=200, headers=None, body=b""):
        self.status = status
        self.headers = headers or {"content-type": "text/plain"}
        self.body = body

    def set_body(self, content, content_type="text/plain"):
        if isinstance(content, str):
            content = content.encode("utf-8")
        self.body = content
        self.headers["content-type"] = content_type

    def set_json(self, obj):
        self.body = json.dumps(obj).encode("utf-8")
        self.headers["content-type"] = "application/json"
