#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bme280
import smbus2
import RPi.GPIO as GPIO

def set_mode():
    GPIO.setmode(GPIO.BCM)

def initialize_bme280():
    port = 1
    address = 0x77  # Adafruit BME280 address. Other BME280s may be different
    bus = smbus2.SMBus(port)
    bme280.load_calibration_params(bus, address)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    #GPIO.setup(gpio_num, GPIO.OUT)
    return bus, address

def temp_press_hum(bus, address):
    bme280_data = bme280.sample(bus, address)
    humidity = bme280_data.humidity
    pressure = bme280_data.pressure
    ambient_temperature = bme280_data.temperature
    fafhrenheite = 9.0 / 5.0 * ambient_temperature + 32
    return fafhrenheite, pressure, humidity

def gpio_init(pin_number):
    GPIO.setup(pin_number, GPIO.OUT)
    gpio_off(pin_number)
    
def gpio_on(pin_number):
    GPIO.output(pin_number, GPIO.LOW)

def gpio_off(pin_number):
    GPIO.output(pin_number, GPIO.HIGH)
    
def gpio_init_input(pin_number):
    GPIO.setup(pin_number, GPIO.IN)#, pull_up_down=GPIO.PUD_DOWN)
    
def gpio_get(pin_number):
    x = GPIO.input(pin_number)
    #print(x)
    if x == GPIO.HIGH:
        return 1
    else:
        return 0

def cleanup():
    GPIO.cleanup()
