
class HttpParserMixin:
    def on_body(self, data):
        self._body += data

    def on_url(self, url):
        self._url = url

    def on_header(self, name, value):
        header = name.decode(self._encoding)
        value = value.decode(self._encoding)
        self._headers[header] = value
