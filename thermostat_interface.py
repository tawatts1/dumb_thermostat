#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 17:14:59 2021

@author: ted
"""
from datetime import datetime, timedelta
from ast import literal_eval
from time import sleep

try:
    from pandas import read_csv
except ImportError:
    pass
try:
    import gpio_utils
except ModuleNotFoundError:
    pass
        
def time_average(t_now, t_prev, old_ave, new_val, mean_time = 3):
    m = (t_now - t_prev).seconds/60
    return (mean_time*old_ave + m*new_val)/(mean_time + m)
    
class realtime_interface():
    def __init__(self, config_file, info_dict):
        with open(config_file, 'r') as file:
            txt = file.read()
        settings = literal_eval(txt)
        
        self.pins = {}
        self.pins['fan']        = settings['gpio_fan']
        self.pins['compressor'] = settings['gpio_compressor']
        self.pins['switch']     = settings['gpio_switch']
        self.pins['led']        = settings['gpio_led']
        
        self.bus, self.address = gpio_utils.initialize_bme280()
        
        gpio_utils.gpio_init(self.pins['fan'])
        gpio_utils.gpio_init(self.pins['compressor'])
        gpio_utils.gpio_init(self.pins['switch'])
        gpio_utils.gpio_init(self.pins['led'])
        
        self.info_dict = {'state':'off', 'time_average':float(settings["time_averaging_minutes"])}
        
        self.pin_states = {'fan':0,
                           'compressor':0,
                           'switch':0,
                           'led':0}
        for i in range(11):
            sleep(.5)
            self.increment()
    def deliver_command(self, cmd):
        if cmd in ('heat', 'cool', 'fan'):
            #make sure switch valve in correct position
            if cmd == 'heat':
                if not self.pin_states['switch']:
                    self.hardware_switch('switch', 1, sleep_sec=60)
            else:
                if self.pin_states['switch']:
                    self.hardware_switch('switch', 0, sleep_sec=60)
                    
            # turn on compressor
            if cmd in ('heat', 'cool'):
                if not self.pin_states['compressor']:
                    self.hardware_switch('compressor', 1)
            # turn on fan
            if not self.pin_states['fan']:
                self.hardware_switch('fan', 1, sleep_sec = 0)
            
        elif cmd == 'off':
            if self.pin_states['compressor']:
                self.hardware_switch('compressor', 0)
            if self.pin_states['fan']:
                self.hardware_switch('fan', 0, sleep_sec = 0)
        
        elif cmd == 0:
            True
        
        else:
            raise ValueError('unexpected command')
        
        
        if cmd != 0:
            self.state = cmd
            
            
    def hardware_switch(self, name, signal, sleep_sec = 10):
        if signal in (0,1):
            if name in ('led', 'compressor', 'fan', 'switch'):
                if signal == 1:
                    gpio_utils.gpio_on(self.pins[name])
                else:
                    gpio_utils.gpio_off(self.pins[name])
                self.pin_states[name] = signal
            else:
                raise ValueError('unexpected hardware name: {0}'.format(name))
        else:
            raise ValueError('unexpected switching signal: {0}'.format(signal))
        
        self.sleep(sleep_sec) 

    def update_info_dict(self):
        temp, press, hum = gpio_utils.temp_press_hum(self.bus, self.address)
        time = datetime.now()
        stable_temp = time_average(time, 
                                   self.settings['time'], 
                                   self.settings['stable_temp'], 
                                   temp, 
                                   mean_time = self.info_dict['time_average'])
        time_str = time.strftime("%H:%M:%S")
        time_float = [int(val) for val in time_str.split(':')]
        time_float = time_float[0] + time_float[1]/60 + time_float[2]/3600
        datetime_str = time.strftime('%y-%m-%d %H:%M:%S')
        weekday = time.strftime('%A')
        state = self.state
        
        self.info_dict['temp'] = temp
        self.info_dict['press'] = press
        self.info_dict['hum'] = hum
        self.info_dict['time'] = time
        self.info_dict['stable_temp'] = stable_temp
        self.info_dict['time_str'] = time_str
        self.info_dict['time_float'] = time_float
        self.info_dict['datetime_str'] = datetime_str
        self.info_dict['weekday'] = weekday
        self.info_dict['state'] = state
        
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
    
    
    
            
        
        
