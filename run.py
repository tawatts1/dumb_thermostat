#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import RPi.GPIO as GPIO
from thermostat import thermostat
#import gpio_utils 
from numpy.random import exponential
from traceback import print_exc
from datetime import datetime

def tuple_to_str(lst, sep=', '):
    out = ''
    for i in range(len(lst)-1):
        out += str(lst[i]) + sep
    out += str(lst[-1])
    return out

therm = thermostat("thermostat.config")#, test_file = 'logs.txt.bak')

try:
    while True:
        therm.sleep(exponential(8)+2)
       
        with open('logs.txt', 'a') as file:
            line = tuple_to_str( therm.check_temp_and_switch() ) + '\n'   
            file.write(line)
            #sleep(4)
        #x=1/0

except:
    with open("errors.txt", 'a') as file:
        file.write("\n===========================\n")
        file.write(datetime.now().strftime('%y-%m-%d %H:%M:%S') + '\n')
        print_exc(file=file)

finally:
    therm.cleanup()

