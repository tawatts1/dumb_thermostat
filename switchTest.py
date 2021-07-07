import bme280
import smbus2
from time import sleep
import RPi.GPIO as GPIO

port = 1
address = 0x77 # Adafruit BME280 address. Other BME280s may be different
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

one = True
two = True
three = True
GPIO.setup(16,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)

while True:
    i = input("type 1 2 or 3")
    if i == '1':
        if one == True:
            print('1 on')
            GPIO.output(16,GPIO.LOW)
            one = False
        else:
            print('1 off')
            GPIO.output(16,GPIO.HIGH)
            one = True
    if i == '2':
        if two == True:
            print('2 on')
            GPIO.output(20,GPIO.LOW)
            two = False
        else:
            print('2 off')
            GPIO.output(20,GPIO.HIGH)
            two = True
    if i == '3':
        if three == True:
            print('3 on')
            GPIO.output(21,GPIO.LOW)
            three = False
        else:
            print('3 off')
            GPIO.output(21,GPIO.HIGH)
            three = True
