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


def setAlsaVolume(payload, client):
    with al_lock:
        try:
            volume = int(payload)
        except:
            if str(payload) == "vol-plus":
                volume = current_volume + 5
            if str(payload) == "vol-minus":
                volume = current_volume - 5
            if str(payload) == "vol-mute":
                if(current_state == "mute"):
                    current_state = "live"
                    volume = current_volume
                else:
                    current_state = "mute"
                    volume = 0
        try:
            xmos = SoundCard(1)
            xmos.loadMixers()
            xmos.setVolume(volume)
            xmos.getVolume()
            if(current_state == "mute"):
                client.publish('hap/alsa/volume', 0)
            else:
                client.publish('hap/alsa/volume', int(volume))
        except:
            print("Volume Set Error")
