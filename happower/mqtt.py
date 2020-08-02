import paho.mqtt.client as mqtt
from happower import pbutton, pled, pmanage
from gpio import setAudioPower, setAmpliPower

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("hap/power/#")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('UTF-8')
    if msg.topic == "hap/power/audio/set":
        setAudioPower(payload)
    if msg.topic == "hap/power/ampli/set":
        setAmpliPower(payload)
    if msg.topic == "hap/power/led/set":
        pled.setLed(payload)
    if msg.topic == "hap/power/set":
        if payload == "On":
            pmanage.OnSequence()
        if payload == "Off":
            pmanage.OffSequence()
    if msg.topic == "hap/power/button/action":
        if payload == "short press":
            pmanage.TogglePower()
    
    print(msg.topic+" "+str(msg.payload))



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
