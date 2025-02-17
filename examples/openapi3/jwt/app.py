#!/usr/bin/env python3
"""
Basic example of a resource server
"""

import time

from jose import jwt, JWTError
from werkzeug.exceptions import Unauthorized

import especifico

JWT_ISSUER = "com.zalando.especifico"
JWT_SECRET = "change_this"
JWT_LIFETIME_SECONDS = 600
JWT_ALGORITHM = "HS256"


def generate_token(user_id):
    timestamp = _current_timestamp()
    payload = {
        "iss": JWT_ISSUER,
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "sub": str(user_id),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        raise Unauthorized from e


def get_secret(user, token_info) -> str:
    return f"""
    You are user_id {user} and the secret is 'wbevuec'.
    Decoded token claims: {token_info}.
    """


def _current_timestamp() -> int:
    return int(time.time())


if __name__ == "__main__":
    app = especifico.FlaskApp(__name__)
    app.add_api("openapi.yaml")
    app.run(port=8080)
