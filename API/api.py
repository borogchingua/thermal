from flask import Flask, request, jsonify
import json
import thermal_control

app = Flask(__name__)


def get_temperature_data():
    temp_data = []
    for zone in thermal_control.sensor_array:
        temp_data.append({"zone_id": zone.zone_ID, "temperature": zone.return_temp(
        ), "status": zone.return_status()})
    return temp_data


@app.route('/get_temperature', methods=['GET'])
def get_temperature():
    temp_data = get_temperature_data()
    return jsonify(temp_data), 200


if __name__ == '__main__':
    app.run(host='137.229.180.236', port=5000)
