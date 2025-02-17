"""
This module centralizes all functionality related to json encoding and decoding in Especifico.
"""

import datetime
import json
from typing import Any, AnyStr, Optional
import uuid


class JSONEncoder(json.JSONEncoder):
    """The default Especifico JSON encoder. Handles extra types compared to the
    built-in :class:`json.JSONEncoder`.

    -   :class:`datetime.datetime` and :class:`datetime.date` are
        serialized to :rfc:`822` strings. This is the same as the HTTP
        date format.
    -   :class:`uuid.UUID` is serialized to a string.
    """

    def default(self, o):
        if isinstance(o, datetime.datetime):
            if o.tzinfo:
                # eg: '2015-09-25T23:14:42.588601+00:00'
                return o.isoformat("T")
            else:
                # No timezone present - assume UTC.
                # eg: '2015-09-25T23:14:42.588601Z'
                return o.isoformat("T") + "Z"

        if isinstance(o, datetime.date):
            return o.isoformat()

        if isinstance(o, uuid.UUID):
            return str(o)

        return json.JSONEncoder.default(self, o)


class Jsonifier:
    """
    Central point to serialize and deserialize to/from JSon in Especifico.
    """

    def __init__(self, json_=json, **kwargs):
        """
        :param json_: json library to use. Must have loads() and dumps() method  # NOQA
        :param kwargs: default arguments to pass to json.dumps()
        """
        self.json = json_
        self.dumps_args = kwargs

    def dumps(self, data, **kwargs):
        """Central point where JSON serialization happens inside Especifico."""
        for k, v in self.dumps_args.items():
            kwargs.setdefault(k, v)
        return self.json.dumps(data, **kwargs) + "\n"

    def loads(self, data: Optional[AnyStr]) -> Optional[Any]:
        """Central point where JSON deserialization happens inside Especifico."""
        if data is None or len(data) == 0:
            return None
        if isinstance(data, bytes):
            data = data.decode()
        return self.json.loads(data)
