#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 17:14:59 2021

@author: ted
"""
from datetime import datetime, timedelta
from time import sleep
try:
    from pandas import read_csv
except ImportError:
    pass
try:
    import gpio_utils
except ModuleNotFoundError:
    pass
        
class realtime_interface():
    def __init__(self, gpio_fan, gpio_compressor, gpio_switch, gpio_led):
        self.gpio_fan        = gpio_fan
        self.gpio_compressor = gpio_compressor
        self.gpio_switch     = gpio_switch
        self.gpio_led        = gpio_led
        
        self.bus, self.address = gpio_utils.initialize_bme280()
        
        gpio_utils.gpio_init(self.gpio_fan)
        gpio_utils.gpio_init(self.gpio_compressor)
        gpio_utils.gpio_init(self.gpio_switch)
        gpio_utils.gpio_init(self.gpio_led)
        self.led_state = 0
        for i in range(11):
            sleep(.5)
            self.increment()
        
    def temp_press_hum(self):
        return gpio_utils.temp_press_hum(self.bus, self.address)
    
    def fan_onoff(self, signal):
        if signal == 1:
            gpio_utils.gpio_on( self.gpio_fan)
        else:
            gpio_utils.gpio_off(self.gpio_fan) 
    def compressor_onoff(self, signal):
        if signal == 1:
            gpio_utils.gpio_on( self.gpio_compressor)
        else:
            gpio_utils.gpio_off(self.gpio_compressor)
    def switch_heatcool(self, heatcool):
        if   heatcool == 'heat':
            gpio_utils.gpio_on( self.gpio_switch)
        elif heatcool == 'cool':
            gpio_utils.gpio_off(self.gpio_switch) 
            
    def time_str(self):
        return datetime.now().strftime("%H:%M:%S")
    def datetime_str(self):
        return datetime.now().strftime('%y-%m-%d %H:%M:%S')
    def datetime_now(self):
        return datetime.now()
    def weekday(self):
        return datetime.now().strftime('%A')
    def time_in_n_minutes_string(self, N):
        return (datetime.now() + timedelta(minutes=N)).strftime("%H:%M:%S")
    def cleanup(self):
        gpio_utils.cleanup()
    def increment(self):
        #used in testing, also used to toggle led
        if self.led_state == 0:
            gpio_utils.gpio_on(self.gpio_led)
        elif self.led_state == 1:
            gpio_utils.gpio_off(self.gpio_led)
        else:
            raise ValueError
        self.led_state = 1-self.led_state
    def sleep(self, n):
        sleep(n)
        
        
#####################################


class testing_interface():
    def __init__(self, fname, pass_time = True, names = None):
        self.df = read_csv(fname, header = 0, sep=', ', engine='python', names = names)
        self.pass_time = pass_time
        self.i = 0
    def temp_press_hum(self):
        data_line = self.df.iloc[self.i]
        return data_line['temp'], data_line['press'], data_line['hum']
    def compressor_onoff(self, signal):
        pass
    def switch_heatcool(self, heatcool):
        pass
    def fan_onoff(self, signal):
        pass
    def time_str(self):
        return self.df.iloc[self.i]['time'].split(' ')[1] #yeah I know
    def datetime_str(self):
        return self.df.iloc[self.i]['time']
    def weekday(self):
        return self.df.iloc[self.i]['weekday']
    def datetime_now(self):
        return datetime.strptime(self.datetime_str(), '%y-%m-%d %H:%M:%S')
    def time_in_n_minutes_string(self, N):
        return self.datetime_now() + timedelta(minutes = N)
    def increment(self):
        self.i += 1
    def cleanup(self):
        pass
    def sleep(self, n):
        pass
    
    
    
            
        
        
