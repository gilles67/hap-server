from gpio import PowerButton, PowerLed, gpio_init, gpio_exit
pbutton = PowerButton()
pled = PowerLed()
from power import PowerManagement
pmanage = PowerManagement()
from mqtt import client

from music import MusicManagement
mmanage = MusicManagement()
