import random
from picamera import PiCamera
from time import sleep
from datetime import datetime
from paho.mqtt import client as mqtt_client
import RPi.GPIO as GPIO

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
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.OUT)

        pwm = GPIO.PWM(11, 50)
        pwm.start(0)

        #pwm.ChangeDutyCycle(8) # right +90 deg position
        #sleep(1)

        pwm.ChangeDutyCycle(7.39)  # neutral position
        sleep(0.8)
        pwm.ChangeDutyCycle(6.75)  # left -90 deg position
        sleep(1.5)

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
