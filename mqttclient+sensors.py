import RPi.GPIO as GPIO
import os
import glob
import time
from time import sleep
import requests
from requests.structures import CaseInsensitiveDict
import random
#from picamera import PiCamera
from datetime import datetime
from paho.mqtt import client as mqtt_client


broker = "broker.emqx.io"
port = 1883
topic = "testmiage2is"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
	def on_message(client, userdata, msg):
		
		print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
		url= "https://api.airtable.com/v0/appbLpHtS6L1K9vRm/IOT_Builds"
		headers = CaseInsensitiveDict()
		headers["Authorization"] = "Bearer keyendZmmLhiFR5jC"  #My own API key
		headers["Content-Type"] = "application/json"

		os.system('modprobe w1-gpio')
		os.system('modprobe w1-therm')

		base_dir = '/sys/bus/w1/devices/'
		device_folder = glob.glob(base_dir + '28*')[0]
		device_file = device_folder + '/w1_slave'

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

		temp_c = read_temp()
		print("temperature (C)", temp_c)

		data = { "records": [{ "id": "recksikdqsttU1TVO","fields":
												{"Temperature": temp_c }}]}
		resp = requests.patch(url, headers=headers, json=data)
		print(resp.text)
		time.sleep(3)

		# Moteur part
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(11, GPIO.OUT)
		pwm=GPIO.PWM(11, 50)
		pwm.start(0)

		for i in range(2):
		  pwm.ChangeDutyCycle(7.39) # neutral position
		  sleep(0.85)
		  pwm.ChangeDutyCycle(6.75) # left -90 deg position
		  sleep(0.8)


		pwm.stop()
		GPIO.cleanup()
		
	client.subscribe(topic)
	client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()

