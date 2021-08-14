from time import sleep
from subprocess import call
import gpio_utils

gpio_utils.set_mode()
N=26
gpio_utils.gpio_init_input(N)
while True:
    sleep(.5)
    if gpio_utils.gpio_get(N) == 1:
        #print('button pressed')
        call('sudo shutdown -h now'.split(' '))
        break
    else:
        #print('nothing detected')
        pass
