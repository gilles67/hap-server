from flask import Flask
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from tinydb import TinyDB
import mpd

app = Flask(__name__)
app.config.from_json('../hapserver-config.json')
Bootstrap(app)
socketio = SocketIO(app, async_mode="eventlet")
mpclient = mpd.MPDClient(use_unicode=True)
tydb = TinyDB('hap.db')

from hapserver import forms, routes, utils, player
