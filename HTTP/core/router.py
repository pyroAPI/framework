
import re

def path_to_regex(path):
    pattern = re.sub(r'{(\w+)}', r'(?P<\1>[^/]+)', path)
    return re.compile(f'^{pattern}$')

def find_handler(routes, request_path):
    for path, handler in routes.items():
        regex = path_to_regex(path)
        match = regex.match(request_path)
        if match:
            return handler, match.groupdict()
    return None, {}
