import alsaaudio
from threading import Thread, RLock

al_lock = RLock()
current_volume = 50
current_state = "live"

class SoundCard:
    def __init__(self, index):
        self.index = index;
        (name, longname) = alsaaudio.card_name(index)
        self.name = name
        self.longname = longname
        self.mixer = None

    def loadMixers(self):
        if self.mixer == None:
            self.mixer = []
            i = 0
            for m in alsaaudio.mixers(cardindex=self.index):
                self.mixer.append(alsaaudio.Mixer(m, id=i ,cardindex=self.index))
                i +=1

    def getVolume(self):
        for m in self.mixer:
            volumes = m.getvolume()
            for i in range(len(volumes)):
                print("Channel %i volume: %i%%" % (i,volumes[i]))

    def setVolume(self, value):
        channel = alsaaudio.MIXER_CHANNEL_ALL
        value = self.__convertVolume(value)
        for m in self.mixer:
            m.setvolume(value, channel)

    def __repr__(self):
        return "[%d]: %s\n(%s)" % (self.index, self.name, self.longname)

    def __convertVolume(self, value):
        if value < 0:
            return 0
        if value <= 8:
            return round((value * 4) + 17)
        if value <= 20:
            return round((value * 1.4) + 40)
        if value <= 28:
            return round((value * 1.1) + 46)
        if value <= 36:
            return round((value * 0.9) + 51)
        if value <= 49:
            return round((value * 0.6) + 62)
        if value <= 59:
            return round((value * 0.4) + 72)
        if value >= 60:
            return round((value * 0.1) + 90)
        if value > 100:
            return 100


def getSoundCards():
    cards = array()
    for i in alsaaudio.card_indexes():
        cards.append(SoundCard(i))
    return cards

def setMixerVolume(volume):
    try:
        xmos = SoundCard(1)
        xmos.loadMixers()
        xmos.setVolume(volume)
        xmos.getVolume()
    except Exception as err:
        print("Volume Set Error")
        print(err)

def saveVolume(volume):
    try:
        fd = open('/etc/hap/alsa/volume', 'w')
        fd.write(str(volume))
        fd.close()
    except Exception as err:
        print("Save volume error")
        print(err)

def resumeVolume():
    try:
        fd = open('/etc/hap/alsa/volume', 'r')
        volume = int(fd.read())
        fd.close()
    except Exception as err:
        volume = 0
        print("Resume volume error")
        print(err)
    return volume


def setAlsaVolume(payload, client):
    global current_state
    global current_volume
    with al_lock:

        if str(payload) == "vol-mute":
            if(current_state == "mute"):
                current_state = "live"
                volume = current_volume
            else:
                current_state = "mute"
                volume = 0
        else:
            try:
                volume = int(payload)
            except:
                if str(payload) == "vol-plus":
                    volume = current_volume + 5
                elif str(payload) == "vol-minus":
                    volume = current_volume - 5
            if volume < 0:
                volume = 0
            if volume > 100:
                volume = 100
            current_volume = volume

        setVolume(volume)

        try:
            if(current_state == "mute"):
                client.publish('hap/alsa/volume', "mute")
            else:
                client.publish('hap/alsa/volume', int(volume))
        except Exception as err:
            print("MQTT Error")
            print(err)

        saveVolume()
