from httptools import HttpRequestParser
from httpparser import HttpParserMixin
from http_objects import Request, Response
import asyncio

class RequestHandler(HttpParserMixin):
    def __init__(self, writer, router=None, encoding='utf-8'):
        self._encoding = encoding
        self._headers = {}
        self._body = b""
        self._url = None
        self._method = None
        self._message_complete = False
        self.writer = writer
        self.parser = HttpRequestParser(self)
        self.router = router
        self.current_request = None
        self.response_sent = asyncio.Event()  # Event to signal response completion

    def feed_data(self, data):
        print(f"Feeding data: {data[:50]}...")
        try:
            a=self.parser.feed_data(data)
            print(a)
        except Exception as e:
            print(f"Parser error: {e}")
            error_response = Response.error("Bad Request", 400)
            self._send_response(error_response)

    def _send_response(self, response):
        response_bytes = response.to_bytes()
        print(f"Sending response: {response_bytes[:50]}...")
        self.writer.write(response_bytes)
        self.response_sent.set()  # Signal that the response has been sent

    def on_message_complete(self):
        print("Message complete detected")
        self._message_complete = True
        method = self.parser.get_method().decode()
        url = self._url.decode(self._encoding)
        
        self.current_request = Request(
            method=method,
            url=url,
            headers=self._headers,
            body=self._body,
            encoding=self._encoding
        )
        
        print(f"Method: {method}")
        print(f"URL: {url}")
        print(f"Path: {self.current_request.path}")
        print(f"Query Params: {self.current_request.query_params}")
        print(f"Headers: {self._headers}")
        print(f"Body: {self._body.decode(self._encoding) if self._body else 'Empty'}")
        
        try:
            if self.router:
                asyncio.create_task(self._dispatch_request())
            else:
                asyncio.create_task(self._default_dispatch(self.current_request))
        except Exception as e:
            print(f"Handler setup error: {e}")
            error_response = Response.error("Internal Server Error", 500)
            self._send_response(error_response)

    async def _dispatch_request(self):
        try:
            print(f"Dispatching: {self.current_request.method} {self.current_request.path}")
            response = await self.router.dispatch(self.current_request)
            self._send_response(response)
        except Exception as e:
            print(f"Dispatch error: {e}")
            error_response = Response.error("Internal Server Error", 500)
            self._send_response(error_response)

    async def _default_dispatch(self, request):
        if request.method == "GET":
            return self.handle_get(request)
        elif request.method == "POST":
            return self.handle_post(request)
        elif request.method == "PUT":
            return self.handle_put(request)
        elif request.method == "DELETE":
            return self.handle_delete(request)
        else:
            return self.handle_method_not_allowed(request)

    def handle_get(self, request):
        print(f"Handling GET request to {request.path}")
        name = request.get_query_param('name', 'World')
        response_data = {
            "message": f"Hello {name}!",
            "method": request.method,
            "path": request.path,
            "query_params": request.query_params
        }
        return Response.json(response_data)

    def handle_post(self, request):
        print(f"Handling POST request to {request.path}")
        if request.is_json():
            json_data = request.json()
            response_data = {
                "message": "POST request received",
                "path": request.path,
                "received_data": json_data,
                "content_type": request.get_header('Content-Type')
            }
        else:
            body_text = request.body.decode(request.encoding) if request.body else ""
            response_data = {
                "message": "POST request received",
                "path": request.path,
                "body": body_text,
                "content_type": request.get_header('Content-Type')
            }
        return Response.json(response_data, status=201)

    def handle_put(self, request):
        print(f"Handling PUT request to {request.path}")
        response_data = {
            "message": "PUT request received",
            "path": request.path,
            "method": request.method
        }
        return Response.json(response_data)

    def handle_delete(self, request):
        print(f"Handling DELETE request to {request.path}")
        response_data = {
            "message": "DELETE request received",
            "path": request.path,
            "method": request.method
        }
        return Response.json(response_data)

    def handle_method_not_allowed(self, request):
        return Response.error(f"Method '{request.method}' not allowed", 405)

    def respond(self, status_code=200, body=b"Hello, World!", content_type="text/plain"):
        status_line = f"HTTP/1.1 {status_code} OK\r\n"
        headers = (
            f"Content-Length: {len(body)}\r\n"
            f"Content-Type: {content_type}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        self.writer.write(status_line.encode() + headers.encode() + body)