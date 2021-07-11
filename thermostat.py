#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 19:56:45 2021

@author: ted
"""
from ast import literal_eval
from datetime import datetime

def write_and_print(error, error_file):
    with open(error_file, 'a') as file:
        file.write('------\n' + \
                    str(datetime.now()) +      \
                    ':\n' +                    \
                    str(error) +               \
                    '\n')
    print(error)

def in_intervals(val, intervals):
    '''
    returns True if time value is inside a list of 2 intervals
    '''
    for interval in intervals:
        if (val < interval[1] and val >= interval[0]) or \
        (interval[1]<interval[0] and (val < interval[1] or val >= interval[0])):
            return True
    return False

class thermostat():
    def __init__(self, config_file, current_mode, error_file = "errors.txt"):
        self.error_file = error_file
        self.mode = current_mode
        #try:
        with open(config_file, 'r') as file:
            txt = file.read()
        settings = literal_eval(txt)
        for mode in ["cool", "heat"]:
            keys = tuple(settings[mode].keys())
            for key in keys:
                div, mod = divmod(float(key), 1)
                div, mod = int(div), int(mod*60)
                time_str = '{:02d}:{:02d}'.format(div, mod)
                settings[mode][time_str] = settings[mode].pop(key)
        self.settings = settings
        #except Exception as error:
        #   write_and_print(error, error_file)

    def get_optimal_temp():


    def l1_switching(self, current_temp_f):
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
        now = datetime.now().strftime("%H:%M")
        mode_settings = self.settings[self.mode]
        times = list(dic.keys())
        times.sort()
        #print(times)
        #L = len(times)
        for i in range(len(times)-1, -1, -1):
            if now > times[i]:
                thermostat_time = times[i]
                break
        else:
            thermostat_time = times[0] # the wee hours of the morning
        #print(thermostat_time)
        #print(dic[thermostat_time])
        sign = {"cool":1,"heat":-1}[self.mode]
        diff = sign*(current_temp_f-dic[thermostat_time])
        if diff > self.settings["threshhold"]:
            out = 1
        elif diff < -self.settings["threshhold"]:
            out = -1
        else:
            out = 0
        return out
    def l2_switching(self, minutes_on):
        pass

    def get_optimal_temp():
        now = datetime.now().strftime("%H:%M")
        times = list(dic.keys())
        times.sort()
        pass

    def get_heating_buffer():
        pass

    def can_heat():
        pass

    def get_cooling_buffer():
        pass

    def can_cool():
        pass

    def evaluate(current_temp_f):
        """
        function that should be called with thermostat.evaluate(f) which
        determines if the AC should be turned on or off.

        Returns
        -------
        1 if element should turn on if not on.
        0 if element should stay in current state
        -1 if element should turn off if it is on.
        """
        optimal_temp = get_optimal_temp()

        temp_differential = optimal_temp - current_temp_f

        if temp_differential > 0 and self.mode == 'heating': # too cold and mode is on heating
            heating_buffer = self.get_heating_buffer()
            if temp_differential > heating_buffer and self.can_heat():
                return 1 # turn on
            elif self.can_heat():
                return 0 # keep heating
            else:
                return -1
        elif self.mode == 'heating':
            return -1

        if temp_differential < 0 and self.mode == 'cooling': # too cold and mode is on cooling
            cooling_buffer = self.get_cooling_buffer()
            if temp_differential > cooling_buffer and self.can_cool():
                return 1 # turn on
            elif self.can_cool():
                return 0 # keep cooling
            else:
                return -1
        elif self.mode == 'cooling':
                return -1














x = thermostat("thermostat.config", "cool")
for t in [75,75.5,7,76.5,77,77.5,78,78.5,79,79.5,80,80.5]:
    print(t, x.l1_switching(t))
