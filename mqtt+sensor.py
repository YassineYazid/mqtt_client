import RPi.GPIO as GPIO
import os
import glob
import time
from time import sleep
import requests
from requests.structures import CaseInsensitiveDict
import random
from datetime import datetime
from paho.mqtt import client as mqtt_client

### CLOUD BROKER SET-UP
broker = "broker.emqx.io"
port = 1883
topic = "testmiage2is"
client_id = f'python-mqtt-{random.randint(0, 100)}'


### ACCESS THE BROKER AND RETURN CLIENT
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

### HANDLE THE SUBSCRIPTION TO TOPIC BUT ALSO "ON MESSAGE" BEHAVIOR


def subscribe(client: mqtt_client):
	def on_message(client, userdata, msg):

		## PRINT WHEN A EACH MESSAGE IS RECEIVED
		print(f"Received msg")

		## TEMPERATURE SENSOR CONFIG
		os.system('modprobe w1-gpio')
		os.system('modprobe w1-therm')
		base_dir = '/sys/bus/w1/devices/'
		device_folder = glob.glob(base_dir + '28*')[0]
		device_file = device_folder + '/w1_slave'

		## GET TEMP FROM THE SENSOR
		def read_temp_raw():
			f = open(device_file, 'r')
			lines = f.readlines()
			f.close()
			return lines

		def read_temp():
			lines = read_temp_raw()
			while lines[0].strip()[-3:] != 'YES':
				time.sleep(0.2)
				lines = read_temp_raw()
			equals_pos = lines[1].find('t=')
			if equals_pos != -1:
				temp_string = lines[1][equals_pos+2:]
				temp_c = float(temp_string) / 1000.0
				return temp_c

		## TEMPERATURE RESULT
		temp_c = read_temp()
		print("temperature (C)", temp_c)

		## DATABASE REQUEST SETUP
		url = "https://api.airtable.com/v0/appbLpHtS6L1K9vRm/IOT_Builds"
		headers = CaseInsensitiveDict()
		headers["Authorization"] = "Bearer keyendZmmLhiFR5jC"  # My own API key
		headers["Content-Type"] = "application/json"

		## UPDATE TEMPERATURE ON DATABASE
		data = {"records": [{"id": "recksikdqsttU1TVO",
                       "fields": {"Temperature": temp_c}}]}
		resp = requests.patch(url, headers=headers, json=data)
		print(resp.text)
		time.sleep(1)

		## MOTOR CONFIG
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(11, GPIO.OUT)
		pwm = GPIO.PWM(11, 50)
		#starting the pulse-width modulation
		pwm.start(0)

		## MOTOR BEHAVIOR (get the water then put it on the recipient)
		for i in range(2):
		  pwm.ChangeDutyCycle(7.39)  # right +90 deg position
		  sleep(0.85) #sleep time to get the angle
		  pwm.ChangeDutyCycle(6.75)  # left -90 deg position
		  sleep(0.8) #sleep time to get the angle

		## STOP AND CLEANUP
		pwm.stop()
		GPIO.cleanup()

	client.subscribe(topic)
	client.on_message = on_message

### SCRIPT CONFIG


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
