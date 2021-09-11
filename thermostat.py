#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 19:56:45 2021

@author: ted
"""
from ast import literal_eval
from datetime import datetime

from max_len_queue import max_len_queue
from bounds_object import temperature_bounds



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

class custodian():
    '''protector of the thermostat. 
    takes input of heating and cooling and does or doesn't to protect thermostat
    '''
    def __init__(self,  config_file, interface, info_dict):
        with open(config_file, 'r') as file:
            txt = file.read()
        settings = literal_eval(txt)
        self.min_on  = settings['min_on']
        self.min_off = settings['min_off']
        self.max_on  = settings['max_on']
        self.info_dict = info_dict
        self.time_state_change = datetime.now()
        self.interface = interface
        
    def update_info_dict(self):
        self.interface.update_info_dict()
    def cleanup(self):
        self.interface.cleanup()
    def sleep(self, n):
        self.interface.sleep(n)
        
    def gen_and_deliver_command(self):
        #not applicable for custodian. 
        pass
        
    def deliver_command(self, cmd):
        '''
        cmd: 'heat'/'cool'/'fan'/0/'off'
        heat, cool, fan should be self exlanatory. 0 means leave in current 
        state. Off means turn it off. 
        interface: can either be another decision class or a pi interface, real
        or virtual. 
        '''
        if cmd not in ('heat', 'cool', 'off', 'fan', 0): #verify valid input
            raise ValueError('unexpected command. cmd should be "heat", "cool", "off", "fan", or 0. ')
            
        dt = (self.info_dict['time'] - self.time_state_change).seconds/60.0
        cmd_out = None
        state = self.info_dict['state']
        if state in ('heat', 'cool'):
            if dt > self.max_on: #if it has been on too long, turn it off
                cmd_out = 'off'
            elif dt < self.min_on: #if it has not gone through cycle, keep on
                cmd_out = 0
            else: #if none of the above are caught, deliver any command
                cmd_out = cmd
        elif state == 'off':
            if dt < self.min_off: #if it has not been off for long enough, keep off
                cmd_out = 0
            else: #deliver original command
                cmd_out = cmd
        else:
           cmd_out = cmd
        #print('{0} => custodian => {1}'.format(cmd, cmd_out))
        self.interface.deliver_command(cmd_out)
        latest_state = self.info_dict['state']
        
        if latest_state != state:
            self.time_state_change = self.info_dict['time']

class forecaster():
    '''precools or preheats at certain times 
    takes input of heating and cooling and does or doesn't to protect thermostat
    '''
    def __init__(self,  config_file, interface, info_dict):
        with open(config_file, 'r') as file:
            txt = file.read()
        settings = literal_eval(txt)
        
        self.settings = settings
        self.info_dict = info_dict
        
        #verify these are in the settings dict. 
        settings['precool']
        settings['preheat']
        settings['weekend_precool']
        settings['weekend_preheat']
        
        self.no_pre_range = settings['no_pre_range'] #temperature range to not precool or preheat
        self.interface = interface
        self.temp_queue = max_len_queue(settings['number_in_queue'])
    
    def update_info_dict(self):
        self.interface.update_info_dict()
    def cleanup(self):
        self.interface.cleanup()
    def sleep(self, n):
        self.interface.sleep(n)
        
    def gen_and_deliver_command(self):
        # is applicable for forecaster, but I would never use it. 
        pass
        
    def deliver_command(self, cmd):
        '''
        cmd: 'heat'/'cool'/'fan'/0/'off'
        heat, cool, fan should be self exlanatory. 0 means leave in current 
        state. Off means turn it off. 
        interface: can either be another decision class or a pi interface, real
        or virtual. 
        '''
        if cmd not in ('heat', 'cool', 'off', 'fan', 0): #verify valid input
            raise ValueError('unexpected command. cmd should be "heat", "cool", "off", "fan", or 0. ')
            
        weekday = self.info_dict['weekday']
        hour = self.info_dict['time_float']
        
        #use median temp over a long period to determine preheat or precool
        median_temp = self.temp_queue.get_percentile(0.5)
        if median_temp:
            #check which mode to use, if any
            if median_temp < self.no_pre_range[0]:
                use_mode = 'heat'
            elif median_temp > self.no_pre_range[1]:
                use_mode = 'cool'
            else: # if we are in a moderate temperature range, don't preheat or cool
                use_mode = False
                cmd_out = cmd
        else: #if there is not any previous data, don't precool or preheat. 
            use_mode = False
            cmd_out = cmd
            
        if use_mode: #if there is a mode to use
            if weekday in ('Saturday', 'Sunday'):
                prefix = 'weekend_pre'
            else:
                prefix = 'pre'
            intervals = self.settings[prefix + use_mode]
            if in_intervals(hour, intervals):
                cmd_out = use_mode
            else:
                cmd_out = cmd
        #print('{0} => forecaster => {1}'.format(cmd, cmd_out))
        self.interface.deliver_command(cmd_out)
   
        
class simple_thermostat():
    def __init__(self,  config_file, interface, info_dict):
        '''

        Parameters
        ----------
        config_file : file name
        interface : pi or something that makes decisions
        info_dict : dictionary
            object that holds most up to date info from hardware whether virtual
            or real. 

        Returns
        -------
        None.

        '''
        with open(config_file, 'r') as file:
            txt = file.read()
        settings = literal_eval(txt)
        
        #verify these settings are there  on initialization
        self.weekday_bounds = temperature_bounds(settings['heat'], 
                                                 settings['cool'])
        self.weekend_bounds = temperature_bounds(settings['weekend_heat'], 
                                                 settings['weekend_cool'])
        
        self.threshhold = settings['threshhold']
        self.info_dict = info_dict
        self.interface = interface
        
    def update_info_dict(self):
        self.interface.update_info_dict()
    def cleanup(self):
        self.interface.cleanup()
    def sleep(self, n):
        self.interface.sleep(n)
    def gen_and_deliver_command(self):
        actual_temp = self.info_dict['stable_temp']
        t = self.info_dict['time_float']
        weekday = self.info_dict['weekday']
        if weekday in ('Saturday', 'Sunday'):
            low, high = self.weekend_bounds.get_bounds(t)
        else:
            low, high = self.weekday_bounds.get_bounds(t)
        
        # if (70 set temp) - (62 actual temp) > 1, 
        if low - actual_temp > self.threshhold:
            cmd_out = 'heat'
        # if (83 actual temp) - (80 set temp) > 1, 
        elif actual_temp - high > self.threshhold:
            cmd_out = 'cool'
        # elif actual temp is in good interval. 
        elif actual_temp > low  + self.threshhold and \
             actual_temp < high - self.threshhold:
            cmd_out = 'off'
        # otherwise the actual temp is pretty close to a set point, so keep in 
        # current state. 
        else:
            cmd_out = 0
        #print('thermostat => {0}'.format(cmd_out))
        self.interface.deliver_command(cmd_out)
    def deliver_command(self, cmd):
        pass
        


if __name__ == "__main__":
    pass

   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   
    
   

