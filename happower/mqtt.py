import paho.mqtt.client as mqtt
import gpio import setAudioPower, setAmpliPower

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("hap/power/#")

def on_message(client, userdata, msg):
    if msg.topic == "hap/power/audio/set":
        setAudioPower(msg.payload)
    if msg.topic == "hap/power/ampli/set":
        setAmpliPower(msg.payload)
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
