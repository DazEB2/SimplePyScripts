#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import sys

from base64 import b64encode

# pip install flask==2.3.3
from flask import Flask, Response, abort

# pip install flask-caching=2.0.2
from flask_caching import Cache

# pip install flask-cors==4.0.0
from flask_cors import CORS

from requests.exceptions import RequestException

sys.path.append("..")
from get_profile_image import get_profile_image


config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
}

app = Flask(__name__)

# tell Flask to use the above defined config
app.config.from_mapping(config)

cache = Cache(app)
CORS(app)


@app.route("/api/get_profile_image/<username>")
@cache.cached()
def api_get_profile_image(username: str):
    try:
        img_data: bytes = get_profile_image(username)
        if not img_data:
            abort(404)

        img_base64 = b64encode(img_data).decode("utf-8")
        return f"data:image/jpg;base64, {img_base64}"

    except RequestException as e:
        return Response(
            response=str(e),
            status=e.response.status_code,
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=50000,
        # TODO: for https
        # ssl_context=("for_https/cert.pem", "for_https/key.pem"),
    )
