import time
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import paho.mqtt.client as paho
from paho import mqtt

#------------------------------------------------------
# User login parameteras: 
theLogin = "aUser"
thePassword = "Abcd1234"
theURL = "d5b09983a26545aea3226f271346f52a.s1.eu.hivemq.cloud"

# Global lists
temperature = []
humidity = []

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
    if msg.topic == "temperature":
        temperature.append(float(msg.payload))
    elif msg.topic == "humidity":
        humidity.append(float(msg.payload))
    else:
        print("ERROR: undefined toipic")

    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

#------------------------------------------------------
# Plotting function 

def update_plot(i):
    """Update the plot based on the new temperature and humidity values"""

    # create the x-axis list
    xTemp = list(range(0,len(temperature)))
    xHum = list(range(0,len(humidity)))

    #clear and plot the new plots
    temp.clear()
    temp.plot(xTemp,temperature)

    hum.clear()
    hum.plot(xHum,humidity)
    
    return




#------------------------------------------------------
# Conect and Setup

reciever = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
reciever.on_connect = on_connect

# enable TLS for secure connection
reciever.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
reciever.username_pw_set(theLogin, thePassword)
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
reciever.connect(theURL, 8883)

# setting callbacks, use separate functions like above for better visibility
reciever.on_subscribe = on_subscribe
reciever.on_message = on_message
reciever.on_publish = on_publish

# Subscribe to topics of the senders
reciever.subscribe("temperature", qos=1)
reciever.subscribe("humidity", qos=1)

#Start the loop
reciever.loop_start()
time.sleep(5) #do nothing for the first 5 seconds for the first values to recieve

#------------------------------------------------------
# Initialize the plot

figure = plt.figure()
temp = figure.add_subplot(2,1,1)
hum = figure.add_subplot(2,1,2)
ani = animation.FuncAnimation(figure,update_plot,interval = 1000)
plt.show()




