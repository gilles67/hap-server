import sys
import os.path

hapserver_path = os.path.abspath(os.path.join(os.path.basename(__file__), '..'))
sys.path.append(hapserver_path)

from hapserver import app, socketio

if __name__ == '__main__':
    socketio.run(app, debug=True)
