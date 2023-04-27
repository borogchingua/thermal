#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import glob
import os
import RPi.GPIO as GPIO

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
sensor_locations = glob.glob('/sys/bus/w1/devices/28-*/w1_slave')
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
# dedicated pins available on raspberry pi
gpio_pin_array = [22, 29, 31, 32, 35, 36, 37, 38]
error_logs = {}


class Temp_zone:
    def __init__(self, sensor_ID, zone_ID, gpio_signal_pin, low_temp_value):
        self.sensor_ID = sensor_ID
        self.zone_ID = zone_ID
        self.gpio_signal_pin = gpio_signal_pin
        self.current_temp = 0
        self.temp_logs = {}

        self.threshold = low_temp_value + (0.125 * low_temp_value)
        self.threshold_flag = False

    def temp_check(self):
        if self.current_temp <= self.threshold:
            self.threshold_flag = True
        elif self.current_temp > self.threshold:
            self.threshold_flag = False

    def gpio_pin_output(self):
        GPIO.output(self.gpio_signal_pin, self.threshold_flag)

    def get_temp(self):
        try:
            with open(self.sensor_ID, 'r') as f:
                lines = f.readlines()
                temp_in_string = lines[1].find('t=')
                temp_string = lines[1][temp_in_string+2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = (temp_c * 1.8) + 32

                self.current_temp = temp_f

                t = time.localtime()
                current_time = time.strftime("%H:%M:%S", t)
                self.temp_logs[current_time] = self.current_temp

        except FileNotFoundError:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            error_logs[current_time] = self.sensor_ID
            print(f"Sensor file for {self.sensor_ID} not found.")

    def return_temp(self):
        return self.current_temp

    def return_status(self):
        return self.threshold_flag


def get_current_temperature():
    for pin in gpio_pin_array:
        GPIO.setup(pin, GPIO.OUT, initial=0)

    sensor_array = []
    sensor_list_size = 0

    for sensor in sensor_locations:
        sensor_list_size += 1

    # Default minimum temperature for all zones
    temp_zone_lows = [20] * sensor_list_size

    for i, sensor in enumerate(sensor_locations):
        sensor_array.append(
            Temp_zone(sensor, (i+1), gpio_pin_array[i], temp_zone_lows[i]))

    # Assuming the first temperature zone is the one you want to use
    return sensor_array[0].return_temp()
