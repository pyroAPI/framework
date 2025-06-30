from parse import parse

def find_handler(routes, request_path):
    for path, handler in routes.items():
        parse_result = parse(path, request_path)
        if parse_result is not None:
            return handler, parse_result.named
    return None, None
