from time import sleep
from subprocess import call
from datetime import datetime
import gpio_utils

fname = "power_record.txt"
with open(fname, 'a') as file:
    file.write(datetime.now().strftime('%y-%m-%d %H:%M:%S') + ',1')

gpio_utils.set_mode()
N=26
gpio_utils.gpio_init_input(N)
while True:
    sleep(.5)
    if gpio_utils.gpio_get(N) == 1:
        #print('button pressed')
        with open(fname, 'a') as file: 
            file.write(datetime.now().strftime('%y-%m-%d %H:%M:%S') + ',1')
        call('sudo shutdown -h now'.split(' '))
        break
    else:
        #print('nothing detected')
        pass
