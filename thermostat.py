#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 19:56:45 2021

@author: ted
"""
from ast import literal_eval
from datetime import datetime, timedelta
import sys
from gpio_utils import gpio_on, gpio_off, initialize_bme280, temp_press_hum
from time import sleep


def write_and_print(error, error_file):
    with open(error_file, 'a') as file:
        file.write('------\n' +
                   str(datetime.now()) +
                   ':\n' +
                   str(error) +
                   '\n')
    print(error)


def in_intervals(val, intervals):
    '''
    returns True if time value is inside a list of 2 intervals
    '''
    for interval in intervals:
        if (val < interval[1] and val >= interval[0]) or \
                (interval[1] < interval[0] and (val < interval[1] or val >= interval[0])):
            return True
    return False


def time_now_string():
    return datetime.now().strftime("%H:%M")
def time_in_n_minutes_string(N):
    return (datetime.now() + timedelta(minutes=N)).strftime("%H:%M")

class thermostat():
    def __init__(self, config_file, current_mode, error_file="errors.txt",test_mode=False):
        self.error_file = error_file
        self.mode = current_mode
        # try:
        with open(config_file, 'r') as file:
            txt = file.read()
        settings = literal_eval(txt)
        for mode in ["cool", "heat"]:
            keys = tuple(settings[mode].keys())
            for key in keys:
                time_str = self.float_to_time(key)
                settings[mode][time_str] = settings[mode].pop(key)
        self.settings = settings
        self.initialize_switches(testing=test_mode)
        self.stable_temp = self.get_temp_press_hum()[0]
        self.state = "off"
        self.time_state_change = datetime.now() - timedelta(minutes = 20)
        self.time_temp_check = datetime.now()
        # except Exception as error:
        #   write_and_print(error, error_file)
    def initialize_switches(self, testing = False):
        for switch in ["gpio_fan", "gpio_compressor"]:
            pin_num = self.settings[switch]
            if testing:
                gpio_on(pin_num)
                sleep(1)
                gpio_off(pin_num)
                sleep(.5)
                gpio_on(pin_num)
                sleep(.5)
            gpio_off(pin_num)
    def initialize_bme(self):
        self.bus, self.address = initialize_bme280(gpio_num=self.settings["gpio_bme"])
    def update_relays(self, signal):
        if signal != 0:
            if self.state == "off" and signal == 1:
                gpio_on(self.settings["gpio_compressor"])
                sleep(10)
                gpio_on(self.settings["gpio_fan"])
                self.state = "on"
                self.time_state_change = datetime.now()
            elif self.state == "on" and signal == -1:
                gpio_off(self.settings["gpio_compressor"])
                sleep(10)
                gpio_off(self.settings["gpio_fan"])
                self.state = "off"
                self.time_state_change = datetime.now()
                
    def get_temp_press_hum(self):
        return temp_press_hum(self.bus, self.address)

    def get_target_temp(self, testing_time = None):
        if testing_time:
            now = testing_time
        else:
            now = time_now_string()
        times = list(
                    self.settings[self.mode].keys()
                        )
        times.sort()
        for i in range(len(times) - 1, -1, -1):
            if now > times[i]:
                thermostat_time = times[i]
                break
        else:
            thermostat_time = times[-1]
        #print("thermostat_time: " + thermostat_time)
        return self.settings[self.mode][thermostat_time]

    def float_to_time(self, flt):
        div, mod = divmod(float(flt), 1)
        div, mod = int(div), int(mod * 60)
        time_str = '{:02d}:{:02d}'.format(div, mod)
        return time_str

    def get_switching_signal(self, current_temp_f, testing_time=None):
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

        target_temp = self.get_target_temp(testing_time=testing_time)
        sign = {"cool": 1, "heat": -1}[self.mode]
        diff = sign * (current_temp_f - target_temp)

        if diff > self.settings["threshhold"]:
            out = 1
        elif diff < -self.settings["threshhold"]:
            out = -1
        else:
            out = 0
        return out

    def get_safe_switching_signal(self, current_temp_f, state, minutes_in_state, testing_time = None):
        ''' if it has run to long, turn it off no matter what
         if it has only been off for a short time minutes, keep it off'''
        if state == 'on':
            if minutes_in_state > self.settings["max_on"]:
                return -1  # make it rest
            elif minutes_in_state < self.settings["min_on"]:
                return 0  # keep it on
        elif state == 'off' and minutes_in_state < self.settings["min_off"]:
            return 0  # keep it off so it can rest

        out = self.l2_switching(current_temp_f)
        if out == 1 and state == 'on':
            out = 0  # No need to send a 1
        elif out == -1 and state == 'off':
            out = 0
        return out
    
    def check_temp_and_switch(self):
        temp, press, hum = self.get_temp_press_hum()
        now = datetime.now()
        minutes_since_last_probe = (now - self.time_temp_check).seconds/60
        minutes_in_state =         (now - self.time_state_change).seconds/60
        self.stable_temp = \
        (self.settings["time_averaging_minutes"]*self.stable_temp + \
                            minutes_since_last_probe*temp)/         \
        (self.settings["time_averaging_minutes"] + minutes_since_last_probe)
        
        switch_signal = self.get_safe_switching_signal(self.stable_temp, 
                                                       self.state, 
                                                       minutes_in_state)
        self.update_relays(switch_signal)
        return self.stable_temp, temp, hum, press, self.state, switch_signal
        
        


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
            
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   

