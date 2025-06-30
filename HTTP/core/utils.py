def parse_headers(raw_headers):
    headers = {}
    for key, value in raw_headers:
        key_str = key.decode("latin-1").lower()
        val_str = value.decode("latin-1")
        if key_str in headers:
            headers[key_str] += ", " + val_str
        else:
            headers[key_str] = val_str
    return headers

def encode_headers(headers):
    return [(k.encode("latin-1"), v.encode("latin-1")) for k, v in headers.items()]
