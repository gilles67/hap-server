import alsaaudio

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
        for m in self.mixer:
            m.setvolume(value, channel)

    def __repr__(self):
        return "[%d]: %s\n(%s)" % (self.index, self.name, self.longname)



def getSoundCards():
    cards = array()
    for i in alsaaudio.card_indexes():
        cards.append(SoundCard(i))
    return cards



xmos = SoundCard(1)
xmos.loadMixers()
xmos.getVolume()
xmos.setVolume(80)
