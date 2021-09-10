#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ast import literal_eval
from numpy.random import exponential
from traceback import print_exc
from datetime import datetime

from thermostat_interface import realtime_interface
from thermostat import custodian, forecaster, simple_thermostat

def tuple_to_str(lst, sep=', '):
    out = ''
    for i in range(len(lst)-1):
        out += str(lst[i]) + sep
    out += str(lst[-1])
    return out

try:
    with open('config/run.config', 'r') as file:
           txt = file.read()
    settings = literal_eval(txt)
    min_time = settings['min_sampling_interval']
    max_time = settings['max_sampling_interval']
    mean_exp = settings['average_interval'] - min_time
    if mean_exp < 0:
        raise ValueError('average interval cannot be smaller than min sampling interval')
    
    shared_dict = {}
    pi = realtime_interface("config/pi.config",           shared_dict)
    l1 = custodian('config/custodian.config',             pi, shared_dict)
    l2 = forecaster('config/forecaster.config',           l1, shared_dict)
    therm = simple_thermostat('config/thermostat.config', l2, shared_dict)
    therm.update_info_dict()
    print(shared_dict)
    while True:
        t = min(exponential(mean_exp) + min_time, max_time)
        therm.sleep(t)
        therm.update_info_dict()
        print(shared_dict)
        therm.gen_and_deliver_command()
        keys = ['weekday', 'datetime_str', 'stable_temp', 'temp', 'press', 'hum', 'state']
        with open('logs.txt', 'a') as file:
            values = [shared_dict[k] for k in keys]
            line = tuple_to_str( values ) + '\n'   
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

