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

while True:
    bme280_data = bme280.sample(bus,address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    ambient_temperature = bme280_data.temperature
    fahrenheit = 9.0/5.0 * ambient_temperature + 32
    print('Humidity: {0}, Temperature: {1}, Pressure: {2}'.format(humidity, fahrenheit, pressure))
    if fahrenheit > 80:
        GPIO.setup(18,GPIO.OUT)
        print("LED on")
        GPIO.output(18,GPIO.HIGH)
    else:
        print("LED off")
        GPIO.output(18,GPIO.LOW)
    sleep(1)

