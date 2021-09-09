#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  5 22:23:23 2021

@author: ted
"""

class max_len_queue():
    def __init__(self, L):
        self.q = []
        self.L = L
    def add(self, obj):
        out = None
        self.q.append(obj)
        if (self.q)>self.L:
            out = self.q.pop(0)
        return out
    def get_max(self):
        return max(self.q)
    def get_min(self):
        return min(self.q)
    def get_ave(self):
        return sum(self.q)/self.L
    def get_percentile(self, p):
        '''
        for median, p=.5 
        for 25th percentile, p=.25
        etc
        '''
        if len(lst)>0:
            lst = self.q.copy()
            lst.sort()
            i = (len(lst)-1)*p//1
            return lst[i]
    
        
    