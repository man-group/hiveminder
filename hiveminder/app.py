from __future__ import absolute_import
from ._flask import Flask, send_file, json, request
import os


_PORT = os.getenv('HIVEMINDER_PORT', 5000)
app = Flask(__name__)


@app.route('/')
def game_page():
    return send_file('static/hiveminder.html')
