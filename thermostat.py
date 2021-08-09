#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 19:56:45 2021

@author: ted
"""
from ast import literal_eval
from datetime import datetime, timedelta
#import sys
#from gpio_utils import gpio_on, gpio_off, initialize_bme280, temp_press_hum
from time import sleep
#import RPi.GPIO as GPIO
from thermostat_interface import realtime_interface, testing_interface

def in_intervals(val, intervals):
    '''
    returns True if time value is inside a list of 2 intervals
    '''
    #print(val, intervals)
    for interval in intervals:
        if (val < interval[1] and val >= interval[0]) or \
                (interval[1] < interval[0] and (val < interval[1] or val >= interval[0])):
            return True
    return False

def in_intervals_time_float(val, intervals):
    '''
    Handles case when val is a time like 22:30:14 and intervals is like [(13.5, 15)]
    '''
    float_val = 0
    pieces = val.split(':')
    if len(pieces) == 2:
        float_val = int(pieces[0]) + int(pieces[1])/60
    elif len(pieces) == 3:
        float_val = int(pieces[0]) + int(pieces[1])/60 + int(pieces[2])/3600
    else:
        raise TypeError
    return in_intervals(float_val, intervals)

class thermostat():
    def __init__(self, config_file, error_file="errors.txt",test_file = '', names = None):
        self.error_file = error_file
        #self.mode = 
        # try:
        with open(config_file, 'r') as file:
            txt = file.read()
        settings = literal_eval(txt)
        for mode in ["cool", "heat", "weekend_cool", "weekend_heat"]:
            keys = tuple(settings[mode].keys())
            for key in keys:
                time_str = self.float_to_time(key)
                settings[mode][time_str] = settings[mode].pop(key)
        self.settings = settings
        if test_file == '':
            self.pi_interface = realtime_interface(self.settings['gpio_fan'],
                                                   self.settings['gpio_compressor'],
                                                   self.settings['gpio_switch'],
                                                   self.settings['gpio_led'])
            self.testing = False
        else:
            self.pi_interface = testing_interface(test_file, names = names)
            self.testing = True
        
        self.stable_temp = self.pi_interface.temp_press_hum()[0]
        self.mode = self.calc_mode(self.stable_temp)
        self.state = "off"
        self.time_state_change = datetime.now() - timedelta(minutes = 20)
        self.time_temp_check = datetime.now()
        self.pi_interface.increment()
        # except Exception as error:
        #   write_and_print(error, error_file)
    
    def sleep(self, n):
        if not self.testing:
            sleep(n)
    
    def calc_mode(self, temp):
        # mode as in 'cool' or 'heat'
        
        if   temp > self.settings['no_compressor'][1]:
            return 'cool'
        elif temp < self.settings['no_compressor'][0]:
            return 'heat'
        else:
            return 0
    def update_mode_relay(self, temp):
        #updates mode relay
        new_mode = self.calc_mode(temp)
        if new_mode: # !=0
            if new_mode != self.mode: # if we need to change it
                self.mode = new_mode
                self.pi_interface.switch_heatcool(new_mode)
                self.sleep(4)
    def update_f_c_relays(self, signal):
        #updates fan and compressor relays
        if signal != 0:
            self.pi_interface.compressor_onoff(signal)
            self.sleep(10)
            self.pi_interface.fan_onoff(signal)
            self.time_state_change = self.pi_interface.datetime_now()
            self.state = {1:'on', -1:'off'}[signal]
    '''def update_all_relays(self, signal, temp):
        self.update_mode_relay(temp)
        if signal != 0:
            self.pi_interface.compressor_onoff(signal)
            self.sleep(10)
            self.pi_interface.fan_onoff(signal)
            self.time_state_change = self.pi_interface.datetime_now()
    '''     #  self.state = {1:'on', -1:'off'}[signal]
            
    def get_target_temp(self):
        now = self.pi_interface.time_str()
        weekday = self.pi_interface.weekday()
        if weekday in ('Saturday', 'Sunday'):
            mode_prefix = 'weekend_'
            times = list(self.settings[mode_prefix + self.mode].keys() )
        else:
            mode_prefix = ''
            times = list(self.settings[mode_prefix + self.mode].keys() )
        times.sort()
        for i in range(len(times) - 1, -1, -1):#start, stop, step
            if now > times[i]:
                thermostat_time = times[i]
                break
        else:
            thermostat_time = times[-1]
        #print("thermostat_time: " + thermostat_time)
        return self.settings[mode_prefix + self.mode][thermostat_time]

    def float_to_time(self, flt):
        div, mod = divmod(float(flt), 1)
        div, mod = int(div), int(mod * 60)
        time_str = '{:02d}:{:02d}'.format(div, mod)
        return time_str

    def get_switching_signal(self, current_temp_f):
        '''
        l1 can be overridden by l2 and l3
        Parameters
        ----------
        current_temp_f : temerature in farenheit

        Returns
        -------
        1 if element should turn on if not on.
        0 if element should stay in current state
        -1 if element should turn off if it is on.
        '''

        target_temp = self.get_target_temp()
        sign = {"cool": 1, "heat": -1}[self.mode]
        diff = sign * (current_temp_f - target_temp)

        if diff > self.settings["threshhold"]:
            out = 1
        elif diff < -self.settings["threshhold"]:
            out = -1
        else:
            out = 0
        return out

    def get_safe_switching_signal(self, current_temp_f, state, minutes_in_state):
        ''' if it has run to long, turn it off no matter what
         if it has only been off for a short time minutes, keep it off'''
        
        if state == 'on':
            ''' #On priorities: 
                1. make sure it has not been on too long
                2. keep it on if it has not been on very long
            '''
            #Make sure it has not been on too long
            if minutes_in_state > self.settings["max_on"]:
                #print(time_now, 'make it rest')
                return -1  # make it rest
            #Make sure it has not been on too short
            elif minutes_in_state < self.settings["min_on"]:
                return 0  # keep it on
            
        elif state == 'off' :
            ''' Off priorities:
                1. keep it off if it has not been off very long
                2. if it is in a precool period, turn it on. 
            '''
            #Make sure it has a chance to rest off
            if minutes_in_state < self.settings["min_off"]:
                return 0  # keep it off so it can rest
            
        out = self.get_switching_signal(current_temp_f)
        if out == 1 and state == 'on':
            out = 0  # No need to send a 1
        elif out == -1 and state == 'off':
            out = 0 # No need to send a -1
        #if out !=0:
        #    print(time_now, out, 'final signal')
        return out
    
    def check_temp_and_switch(self):
        temp, press, hum = self.pi_interface.temp_press_hum() 
        now = self.pi_interface.datetime_now()
        minutes_since_last_probe = (now - self.time_temp_check).seconds/60
        minutes_in_state =         (now - self.time_state_change).seconds/60
        self.time_temp_check = now
        self.stable_temp = \
        (self.settings["time_averaging_minutes"]*self.stable_temp + \
                            minutes_since_last_probe*temp)/         \
        (self.settings["time_averaging_minutes"] + minutes_since_last_probe)
        
        self.update_mode_relay(self.stable_temp)
        switch_signal = self.get_safe_switching_signal(self.stable_temp, 
                                                       self.state, 
                                                       minutes_in_state)
        self.update_f_c_relays(switch_signal) # fan, compressor relays
        
        weekday = self.pi_interface.weekday()
        datetime_str = self.pi_interface.datetime_str()
        self.pi_interface.increment()
        return weekday, datetime_str, self.stable_temp, temp, hum, press, self.state, switch_signal
    def cleanup(self):
        self.pi_interface.cleanup()
        


def test1():
    x = thermostat("thermostat.config", "cool")
    for t in [75, 75.5, 7, 76.5, 77, 77.5, 78, 78.5, 79, 79.5, 80, 80.5]:
        print(t, x.l1_switching(t))
   


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    therm = thermostat("thermostat.config", "cool")
    x = []
    y = []
    for i in range(24*60):
        h, m = divmod(i, 60)
        time_str = '{:02d}:{:02d}'.format(h,m)
        x.append(i/60)
        y.append(therm.get_target_temp(testing_time = time_str))
        
    plt.plot(x, y)
    plt.show()
            
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   

