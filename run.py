#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO
from thermostat import thermostat, write_and_print
import gpio_utils 
from numpy.random import normal

def get_date_and_weekday():
    ''' returns list of date string and day of week string:
        ['21-07-12 22:20', 'Monday']'''
    return datetime.now().strftime('%y-%m-%d %H:%M:%Sbutt%A').split('butt')
    
#initial conditions: 
mode = 'cool'
therm = thermostat("thermostat.config", mode, test_mode = True)

try:
    while True:
        sleep(abs(normal(10,3)))
        time, weekday = get_date_and_weekday()
    
        print("LED on")
        gpio_utils.gpio_on(18)
        sleep(.5)
        print("LED off")
        gpio_utils.gpio_off(18)

        stable_temp, temp, hum, press, state, switch_signal = therm.check_temp_and_switch()        

        with open('logs.txt', 'a') as file:
            line = '{0}, {1}, {2:.3f}, {3:.3f}, {4:.3f}, {5:.1f}, {6}, {7}\n'.format(
                weekday, time, stable_temp, temp, hum, press, state, switch_signal)
            file.write(line)
        #sleep(4)
except Exception as error:
    write_and_print(error, "errors.txt")
finally:
    GPIO.cleanup
