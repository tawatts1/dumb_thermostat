#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import RPi.GPIO as GPIO
from thermostat import thermostat, write_and_print
#import gpio_utils 
from numpy.random import normal

#initial conditions: 
mode = 'cool'
therm = thermostat("thermostat.config", mode)#, test_file = 'logs.txt.bak')

#try:
while True:
    therm.sleep(abs(normal(8,4))+2)
    
    #print("LED on")
    #gpio_utils.gpio_on(18)
    therm.sleep(.5)
    #print("LED off")
    #gpio_utils.gpio_off(18)

    weekday, time, stable_temp, temp, hum, press, state, switch_signal = therm.check_temp_and_switch()        

    with open('logs.txt', 'a') as file:
        line = '{0}, {1}, {2:.3f}, {3:.3f}, {4:.3f}, {5:.1f}, {6}, {7}\n'.format(
            weekday, time, stable_temp, temp, hum, press, state, switch_signal)
        file.write(line)
        #sleep(4)
'''
except Exception as error:
    write_and_print(error, "errors.txt")
finally:
    therm.cleanup()
'''
