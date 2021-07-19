#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bme280
import smbus2
import RPi.GPIO as GPIO


def initialize_bme280(gpio_num=18):
    port = 1
    address = 0x77  # Adafruit BME280 address. Other BME280s may be different
    bus = smbus2.SMBus(port)
    bme280.load_calibration_params(bus, address)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(gpio_num, GPIO.OUT)
    return bus, address

def temp_press_hum(bus, address):
    bme280_data = bme280.sample(bus, address)
    humidity = bme280_data.humidity
    pressure = bme280_data.pressure
    ambient_temperature = bme280_data.temperature
    fafhrenheite = 9.0 / 5.0 * ambient_temperature + 32
    return fafhrenheite, pressure, humidity

def gpio_on(pin_number):
    GPIO.output(pin_number, GPIO.LOW)

def gpio_off(pin_number):
    GPIO.output(pin_number, GPIO.HIGH)
