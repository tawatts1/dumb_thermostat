#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 14:10:23 2021

@author: ted
"""

import gpio_utils
b,a = gpio_utils.initialize_bme280()
print(gpio_utils.temp_press_hum(b,a))
