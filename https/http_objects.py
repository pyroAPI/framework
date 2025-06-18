# New file: http_objects.py
import json
from urllib.parse import urlparse, parse_qs


class Request:
    def __init__(self, method, url, headers, body, encoding='utf-8'):
        self.method = method
        self.raw_url = url
        self.headers = headers
        self.body = body
        self.encoding = encoding
        
        # Parse URL components
        parsed_url = urlparse(url)
        self.path = parsed_url.path
        self.query_params = parse_qs(parsed_url.query)
        self.fragment = parsed_url.fragment
        
        # Parse body if JSON
        self._json_data = None
        if self.is_json():
            try:
                self._json_data = json.loads(body.decode(encoding))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._json_data = None
    
    def is_json(self):
        """Check if request has JSON content type"""
        content_type = self.headers.get('Content-Type', '').lower()
        return 'application/json' in content_type
    
    def json(self):
        """Get JSON data from request body"""
        return self._json_data
    
    def get_query_param(self, key, default=None):
        """Get query parameter value"""
        values = self.query_params.get(key, [])
        return values[0] if values else default
    
    def get_header(self, key, default=None):
        """Get header value (case insensitive)"""
        for header_key, value in self.headers.items():
            if header_key.lower() == key.lower():
                return value
        return default


class Response:
    def __init__(self, body="", status=200, headers=None, content_type="text/plain"):
        self.body = body
        self.status = status
        self.headers = headers or {}
        self.content_type = content_type
        
        # Set default content type if not provided
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = content_type
    
    def to_bytes(self):
        """Convert response to bytes for sending over socket"""
        # Convert body to bytes if it's a string
        if isinstance(self.body, str):
            body_bytes = self.body.encode('utf-8')
        elif isinstance(self.body, dict) or isinstance(self.body, list):
            # Auto-convert dict/list to JSON
            body_bytes = json.dumps(self.body).encode('utf-8')
            self.headers['Content-Type'] = 'application/json'
        else:
            body_bytes = self.body
        
        # Build HTTP response
        status_line = f"HTTP/1.1 {self.status} {self._get_status_text()}\r\n"
        
        # Add content length
        self.headers['Content-Length'] = str(len(body_bytes))
        self.headers['Connection'] = 'close'
        
        # Build headers
        headers_str = ""
        for key, value in self.headers.items():
            headers_str += f"{key}: {value}\r\n"
        
        # Combine all parts
        response = status_line + headers_str + "\r\n"
        return response.encode('utf-8') + body_bytes
    
    def _get_status_text(self):
        """Get status text for common status codes"""
        status_texts = {
            200: "OK",
            201: "Created",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            500: "Internal Server Error"
        }
        return status_texts.get(self.status, "Unknown")
    
    @classmethod
    def json(cls, data, status=200, headers=None):
        """Create a JSON response"""
        return cls(
            body=data,
            status=status,
            headers=headers,
            content_type="application/json"
        )
    
    @classmethod
    def html(cls, html_content, status=200, headers=None):
        """Create an HTML response"""
        return cls(
            body=html_content,
            status=status,
            headers=headers,
            content_type="text/html"
        )
    
    @classmethod
    def error(cls, message, status=500, headers=None):
        """Create an error response"""
        return cls(
            body={"error": message, "status": status},
            status=status,
            headers=headers,
            content_type="application/json"
        )