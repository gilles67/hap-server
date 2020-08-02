import mpd
import eventlet
from threading import Lock
from flask_socketio import emit
from tinydb import Query
from hapserver import socketio, mpclient, tydb, app

mpd_thread = None
mpd_thread_lock = Lock()

@socketio.on('action')
def action_socket(message):
    try:
        mpclient.ping()
    except Exception as e:
        mpclient.connect(app.config['MPC_SERVER'], int(app.config['MPC_PORT']))

    status = mpclient.status()
    if 'action' in message:
        if message['action'] == 'play':
            if 'radio' in message:
                Webradio = Query()
                webra = tydb.get(Webradio.id == message['radio'])
                mpclient.clear()
                mpclient.add(webra['url'])
                mpclient.play(0)
            mpclient.pause(0)
        if message['action'] == 'pause':
            mpclient.pause(1)

        if message['action'] == 'stop':
            mpclient.stop()

        if message['action'] == 'vol-plus':
            vol = int(status['volume']) + 10
            if vol > 100:
                vol = 100
            mpclient.setvol(vol)

        if message['action'] == 'vol-minus':
            if 'volume' in status:
                vol = int(status['volume']) - 10
                if vol < 0:
                    vol = 0
            else:
                vol = 10
            mpclient.setvol(vol)

        if message['action'] == 'vol-mute':
            mpclient.setvol(0)

        if message['action'] == 'volume':
            if 'volume' in message:
                vol = int(message['volume'])
                if vol > 100:
                    vol = 100
                if vol < 0:
                    vol = 0
                mpclient.setvol(vol)

    emit('action_reply',{ 'status': mpclient.status(), 'song': mpclient.currentsong()})

@socketio.on('connect')
def test_connect():
    global mpd_thread
    with mpd_thread_lock:
        if mpd_thread is None:
            mpd_thread = socketio.start_background_task(follow_mpclient)
            app.logger.info('mpd_thread start : follow_mpclient')

def follow_mpclient():
    mpdcls = mpd.MPDClient(use_unicode=True)
    will_continue = True
    while will_continue:
        try:
            socketio.sleep(1)
            mpdcls.ping()
            #mpdcls.idle()
            socketio.emit('action_reply',{ 'status': mpdcls.status(), 'song': mpdcls.currentsong()})
            #print (mpdcls.status())
            #print (mpdcls.currentsong())
            #print (mpdcls.stats())
        except Exception as e:
            will_continue = False
            app.logger.info('mpd_thread break')
            if type(e) == mpd.base.ConnectionError:
                will_continue = True
                mpdcls.connect(app.config['MPC_SERVER'], int(app.config['MPC_PORT']))
                app.logger.info('mpd_thread connection error continue')
            else:
                print (e)
            app.logger.info('mpd_thread break, continue=%s', will_continue)
    app.logger.info('mpd_thread exited')
    mpdcls.close()
