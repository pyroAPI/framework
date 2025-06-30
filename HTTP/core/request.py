class Request:
    def __init__(self, method, path, headers, body, query):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.query = query
