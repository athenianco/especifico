"""
This module defines interfaces for requests and responses used in Especifico for authentication,
validation, serialization, etc.
"""


class EspecificoRequest:
    """Especifico interface for a request."""

    __slots__ = (
        "url",
        "method",
        "path_params",
        "query",
        "headers",
        "form",
        "body",
        "_json",
        "json_getter",
        "files",
        "context",
        "cookies",
    )

    def __init__(
        self,
        url,
        method,
        path_params=None,
        query=None,
        headers=None,
        form=None,
        body=None,
        json_getter=None,
        files=None,
        context=None,
        cookies=None,
    ):
        self.url = url
        self.method = method
        self.path_params = path_params or {}
        self.query = query or {}
        self.headers = headers or {}
        self.form = form or {}
        self.body = body
        self._json = None
        self.json_getter = json_getter
        self.files = files
        self.context = context if context is not None else {}
        self.cookies = cookies or {}

    @property
    def json(self):
        if self._json is None:
            self._json = self.json_getter()
        return self._json


class EspecificoResponse:
    """Especifico interface for a response."""

    __slots__ = (
        "status_code",
        "mimetype",
        "content_type",
        "body",
        "headers",
        "is_streamed",
    )

    def __init__(
        self,
        status_code=200,
        mimetype=None,
        content_type=None,
        body=None,
        headers=None,
        is_streamed=False,
    ):
        self.status_code = status_code
        self.mimetype = mimetype
        self.content_type = content_type
        self.body = body
        self.headers = headers or {}
        self.is_streamed = is_streamed
