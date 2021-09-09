#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 19:52:23 2021

@author: ted
"""

class temperature_bounds():
    def __init__(self, lower, upper, mod_ = 24):
        self.lower = lower
        self.upper = upper
        self.mod_ = mod_
        self.lower_times_sorted = list(lower.keys())
        self.lower_times_sorted.sort()
        self.upper_times_sorted = list(upper.keys())
        self.upper_times_sorted.sort()
        
        #verify validity:
        for x in range(0, 4000):
            t = 3.14159265*x % mod_
            a,b = self.get_bounds(t)
            if b<a:
                raise ValueError('{0} gets bounds {1}, {2}'.format(t,a,b))
    def get_bounds(self, t):
        if t > self.mod_:
            raise ValueError

        for i in range(len(self.lower_times_sorted) -1, -1, -1): #start, stop, step
            if t > self.lower_times_sorted[i]:
                lower_key = self.lower_times_sorted[i]
                break
        else:
            lower_key = self.lower_times_sorted[-1]
            
        for i in range(len(self.upper_times_sorted) -1, -1, -1): #start, stop, step
            if t > self.upper_times_sorted[i]:
                upper_key = self.upper_times_sorted[i]
                break
        else:
            upper_key = self.upper_times_sorted[-1]
            
        return self.lower[lower_key], self.upper[upper_key]

if __name__ == '__main__':
    cool = {8:80, 13.5:74, 15:81, 20:78, 23:76}
    heat = {7:69, 8:70, 12.75:71, 15:69, 20:71, 22.5:65}
    
    b = temperature_bounds(heat, cool)
    
    for t in [1, 10,12, 15, 16, 19, 20.01, 23.5]:
        print(t, b.get_bounds(t))
    
            