import bme280
import smbus2
from time import sleep
import RPi.GPIO as GPIO
import thermostat

port = 1
address = 0x77 # Adafruit BME280 address. Other BME280s may be different
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)


def led_condition(f):
    if round((f%.1)*1111000)%7 == 0:
        return True
    return False

while True:
    bme280_data = bme280.sample(bus,address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    ambient_temperature = bme280_data.temperature
    fafhrenheite = 9.0/5.0 * ambient_temperature + 32
    print('Humidity: {0}, Temperature: {1}, Pressure: {2}'.format(humidity, fafhrenheite, pressure))
    if led_condition(fafhrenheite):
        GPIO.setup(18,GPIO.OUT)
        print("LED on")
        GPIO.output(18,GPIO.HIGH)
    else:
        print("LED off")
        GPIO.output(18,GPIO.LOW)

    mode = 'cool'
    current_temp_f = ambient_temperature #
    current_state = 'off'# on/off
    minutes_in_state = 0 #

    therm = thermostat("thermostat.config", mode)
    code = therm.l2_switching(current_temp_f, current_state, minutes_in_state)
    print(code)
    with open('logs.txt', a) as file:
        file.write('Humidity: {0}, Temperature: {1}, Pressure: {2}, Code: {3}'.format(humidity, fafhrenheite, pressure, code))
        file.write('\n')
    sleep(5)
