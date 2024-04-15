import time
import random
import paho.mqtt.client as paho
from paho import mqtt

#------------------------------------------------------
# User login parameteras: 
theLogin = "aSender1"
thePassword = "Abcd1234"
theURL = "d5b09983a26545aea3226f271346f52a.s1.eu.hivemq.cloud"

#------------------------------------------------------
# Definition of response 

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

#------------------------------------------------------
# Conect and Setup

sender1 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
sender1.on_connect = on_connect

# enable TLS for secure connection
sender1.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
sender1.username_pw_set(theLogin, thePassword)
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
sender1.connect(theURL, 8883)

# setting callbacks, use separate functions like above for better visibility
sender1.on_subscribe = on_subscribe
sender1.on_message = on_message
sender1.on_publish = on_publish

#-----------------------------------------------------
# Loop of sending random data to a unique topc every 3 seconds 

while True:
    sender1.loop_start()
    sender1.publish("temperature", payload=random.uniform(10.0,120.0), qos=1)
    sender1.loop_stop()
    time.sleep(3)

