from mqttclient import MQTTClient
import network
import sys
import time

import machine
from mpu9250_new import MPU9250
from machine import I2C, Pin
from board import SDA, SCL

# Initialzing the variables used. This is where you would hard code the limit of gumballs to allow per whatever you'd like
limit=1
gumball = 0

# Check wifi connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
ip = wlan.ifconfig()[0]
if ip == '0.0.0.0':
    print("no wifi connection")
    sys.exit()
else:
    print("connected to WiFi at IP", ip)

# Set up Adafruit connection
adafruitIoUrl = 'io.adafruit.com'
adafruitUsername = 'cacoelho'
adafruitAioKey = 'KEY'

# Define callback function
def sub_cb(topic, msg):
    print((topic, msg))

# Connect to Adafruit server
print("Connecting to Adafruit")
mqtt = MQTTClient(adafruitIoUrl, port='1883', user=adafruitUsername, password=adafruitAioKey)
time.sleep(0.5)
print("Connected!")

# This will set the function sub_cb to be called when mqtt.check_msg() checks
# that there is a message pending
mqtt.set_callback(sub_cb)



MPU9250._chip_id = 113 # new mpu9250

i2c = I2C(id=0, scl=Pin(SCL), sda=Pin(SDA), freq=400000)
imu = MPU9250(i2c)

feedName = "cacoelho/feeds/me100-project"

# I've found that the gyro values in the z direction have been the most consistent and reliable
def pvalues(Timer):

    print(imu.gyro.z)
    print('')

tm = machine.Timer(1)
tm.init(period=750, mode=tm.PERIODIC, callback=pvalues)
# Send test message

# This runs the data checking of the gyroscope in the z direction for an amount of seconds specified in the range
for i in range(0, 100):
    mqtt.check_msg()
    time.sleep(1)

    if imu.gyro.z>5 or imu.gyro.z<-5:
        gumball=gumball+1
        time.sleep(0.5)
    if gumball>limit:
        testMessage = "Limit Reached"
        mqtt.publish(feedName,testMessage)
        print("Published {} to {}.".format(testMessage,feedName))
        mqtt.subscribe(feedName)
        gumball = limit
        time.sleep(3)
