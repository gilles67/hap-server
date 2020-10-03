import sys
import os.path

happower_path = os.path.abspath(os.path.join(os.path.basename(__file__), '..'))
sys.path.append(happower_path)

import atexit
from happower import client, pbutton, pled, pmanage, gpio_init, gpio_exit

def exit_seq():
    pb.stop()

if __name__ == '__main__':
    try:
        gpio_init()
        client.connect("192.168.1.63", 1883, 60)
        pbutton.setClient(client)
        pbutton.start()
        pled.start()
        pmanage.setClient(client)
        pmanage.start()
        mmanage.setClient(client)
        mmanage.start()
        client.loop_forever()
    except KeyboardInterrupt:
        pbutton.stop()
        pled.stop()
        pmanage.stop()
        mmanage.stop()
        client.disconnect()
        gpio_exit()
