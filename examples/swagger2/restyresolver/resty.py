#!/usr/bin/env python
import logging

import especifico
from especifico.resolver import RestyResolver

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    app = especifico.FlaskApp(__name__)
    app.add_api(
        "resty-api.yaml",
        arguments={"title": "RestyResolver Example"},
        resolver=RestyResolver("api"),
    )
    app.run(port=9090)
