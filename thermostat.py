#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 19:56:45 2021

@author: ted
"""
from ast import literal_eval
from datetime import datetime
import sys


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


class thermostat():
    def __init__(self, config_file, current_mode, error_file="errors.txt"):
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
        # except Exception as error:
        #   write_and_print(error, error_file)

    def time_now(self):
        return datetime.now().strftime("%H:%M")

    def get_target_temp(self):
        now = self.time_now()
        dic = self.settings[self.mode]
        times = list(dic.keys())
        times.sort()
        # print(times)
        #L = len(times)
        for i in range(len(times) - 1, -1, -1):
            if now > times[i]:
                thermostat_time = times[i]
                break
        else:
            thermostat_time = times[0]
        return self.settings[self.mode][thermostat_time]

    def float_to_time(self, flt):
        div, mod = divmod(float(flt), 1)
        div, mod = int(div), int(mod * 60)
        time_str = '{:02d}:{:02d}'.format(div, mod)
        return time_str

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

    def l2_switching(self, current_temp_f, state, minutes_in_state):
        # if it has run to long, turn it off no matter what
        # if it has only been off for a short time minutes, keep it off
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


def test1():
    x = thermostat("thermostat.config", "cool")
    for t in [75, 75.5, 7, 76.5, 77, 77.5, 78, 78.5, 79, 79.5, 80, 80.5]:
        print(t, x.l1_switching(t))


if __name__ == "__main__":
    mode = sys.argv[1]
    current_temp_f = sys.argv[2]
    current_state = sys.argv[3]  # on/off
    minutes_in_state = sys.argv[4]

    therm = thermostat("thermostat.config", mode)
    print(therm.l2_switching(current_temp_f, current_state, minutes_in_state))


x = thermostat("thermostat.config", "cool")
for t in [75, 75.5, 7, 76.5, 77, 77.5, 78, 78.5, 79, 79.5, 80, 80.5]:
    print(t, x.l1_switching(t))
