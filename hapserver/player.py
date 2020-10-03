import mpd
import eventlet
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from threading import Lock
from flask_socketio import emit
from tinydb import Query
from hapserver import socketio, mpclient, tydb, app

mpd_thread = None
mpd_thread_lock = Lock()

mqttcls = None
mqtt_thread = None

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
            publish.single("hap/alsa/volume/set", "vol-plus", hostname=app.config['MPC_SERVER'])

        if message['action'] == 'vol-minus':
            publish.single("hap/alsa/volume/set", "vol-minus", hostname=app.config['MPC_SERVER'])

        if message['action'] == 'vol-mute':
            publish.single("hap/alsa/volume/set", "vol-mute", hostname=app.config['MPC_SERVER'])
        if message['action'] == 'volume':
            if 'volume' in message:
                publish.single("hap/alsa/volume/set", int(message['volume']), hostname=app.config['MPC_SERVER'])
    emit('action_reply',{ 'status': mpclient.status(), 'song': mpclient.currentsong()})

@socketio.on('connect')
def test_connect():
    global mpd_thread
    global mqtt_thread
    with mpd_thread_lock:
        if mpd_thread is None:
            mpd_thread = socketio.start_background_task(follow_mpclient)
            app.logger.info('[MPD] mpd_thread start : follow_mpclient')
        if mqtt_thread is None:
            mqtt_thread = socketio.start_background_task(follow_happower)
            app.logger.info('[MQTT] mqtt_thread start : follow_happower')

## MPD

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

## MQTT (happower)

def mqtt_connect(client, userdata, flags, rc):
    app.logger.info('mqtt_thread connect, code=%s', rc)
    client.subscribe("hap/power/#")
    client.subscribe("hap/alsa/#")

def mqtt_message(client, userdata, msg):
    payload = msg.payload.decode('UTF-8')
    app.logger.info('mqtt_thread message, topic=%s, payload=%s', msg.topic, payload)
    socketio.emit('mqtt_reply', {'topic':msg.topic, 'payload': payload })

def follow_happower():
    mqttcls = mqtt.Client()
    mqttcls.on_connect = mqtt_connect
    mqttcls.on_message = mqtt_message
    mqttcls.connect(app.config['MPC_SERVER'], 1883, 60)
    will_continue = True
    while will_continue:
        try:
            #socketio.sleep(1)
            mqttcls.loop()
        except:
            will_continue = False
            app.logger.info('mqtt_thread break')
