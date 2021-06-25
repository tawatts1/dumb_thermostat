from flask import Flask
from flask import jsonify
from flask import render_template
from flask import url_for
import bme280
import smbus2
from time import sleep

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

port = 1
address = 0x77
bus = smbus2.SMBus(port)
bme280.load_calibration_params(bus,address)


# with app.test_request_context():
#     url_for('static', filename='style.css')
#     url_for('static', filename='app.js')


@app.route('/api')
def api():
    bme280_data = bme280.sample(bus,address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    ambient_temperature = bme280_data.temperature
    fahrenheit = 9.0/5.0 * ambient_temperature + 32

    return jsonify({
        "temperature": { "C": ambient_temperature, "F": fahrenheit },
        "pressure": { "mb": pressure },
        "humidity": humidity
    })
#
# @app.route('/')
# def home():
#     return render_template('./home.html')
