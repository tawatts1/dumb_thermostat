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

fname = "data0.txt"

while True:
    bme280_data = bme280.sample(bus,address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    ambient_temperature = bme280_data.temperature
    faf = 9.0/5.0 * ambient_temperature + 32
    string = '{0},\t{1},\t{2}\n'.format(faf,humidity,pressure)
    print(string + '             ', end = '\r')
    with open(fname, 'a') as file:
        file.write(string)
    sleep(1)

