#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 22:14:44 2021

@author: ted
Adapted from:
https://stackoverflow.com/questions/50388069/check-status-if-raspberry-pi-is-connected-to-any-wifi-network-not-internet-nece

"""

import subprocess
from time import sleep
from datetime import datetime
from traceback import print_exc

def get_network_status():
    ps = subprocess.Popen(['iwconfig'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout).decode('ascii')
        if 'BM FBI' in output:
            connected = True
        else:
            with open('wifi_log.txt', 'a') as file:
                file.write(output + '\n')
            connected = False
    except subprocess.CalledProcessError:
        connected = False
    return connected

def restart_wifi():
    t = datetime.now()
    subprocess.run('sudo wpa_cli -i wlan0 reconfigure'.split(' '))
    sleep(50)
    with open('wifi_log.txt', 'a') as file:
        file.write('restarted at {0}'.format(t.strftime('%y-%m-%d %H:%M:%S\n')))
    
    
    

if __name__ == '__main__':
    try:
        while True:
            sleep(20)
            if not get_network_status():
                restart_wifi()
    except:
        with open("errors.txt", 'a') as file:
            file.write("\n===========================\n")
            file.write(datetime.now().strftime('%y-%m-%d %H:%M:%S\n'))
            print_exc(file=file)
        
        