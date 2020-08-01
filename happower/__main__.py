import sys
import os.path

happower_path = os.path.abspath(os.path.join(os.path.basename(__file__), '..'))
sys.path.append(happower_path)

import atexit
from happower import client, PowerButton, gpio_init, gpio_exit

def exit_seq():
    pb.stop()

if __name__ == '__main__':
    try:
        gpio_init()
        client.connect("192.168.1.63", 1883, 60)
        pb = PowerButton(client)
        pb.start()
        client.loop_forever()
    except KeyboardInterrupt:
        pb.stop()
        client.disconnect()
        gpio_exit()
