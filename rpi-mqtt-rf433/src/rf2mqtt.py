#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__  = "Kadda SAHNINE"
__contact__ = "ksahnine@gmail.com"
__license__ = 'GPL v3'

import getopt
import logging
import os
import paho.mqtt.client as mqtt
import RPi.GPIO as io
import signal
import sys
import time
from libs.rfsniffer import RFSniffer

client = mqtt.Client()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
mqttHost = os.getenv('MQTT_HOST', 'localhost')
mqttPort = int(os.getenv('MQTT_PORT', '1883'))
mqttSubTopic = os.getenv('MQTT_SUB_TOPIC', '/rpi/rf433/in')
mqttPubTopic = os.getenv('MQTT_PUB_TOPIC', '/rpi/rf433/out')

def usage():
    """
    Display usage
    """
    sys.stderr.write( "Usage: rf2mqtt.py [-r <recvPin>    | --receive-pin=<recvPin>\n"+
          "                   [-s <sendPin>     | --send-pin=<sendPin>\n"+
          "                   [-P <topic>       | --publish-topic=<topic>\n"+
          "                   [-S <topic>       | --subscribe-topic=<topic>\n"+
          "                   [-H <mqtt-host>   | --mqtt-host=<mqtt-host>\n"+
          "                   [-p <mqtt-port>   | --mqtt-port=<mqtt-port>\n"+
          "                   [-l <logLevel>    | --log-level=<logLevel>\n")

def clean(signum, frame):
     """
     Signal handler (SIGTERM / SIGINT)
     """
     logger.info("Disconnecting from the broker")
     client.disconnect()
     sys.exit(signum)

def connect():
    """
    Connect to the MQTT broker and subscribe to topic
    """
    rc = client.connect(mqttHost, mqttPort, 60)
    if rc != 0:
        logger.info("Connection failed with error code %s. Retrying", result)
        time.sleep(10)
        connect()
        sniffer = RFSniffer(client, mqttPubTopic, logLevel)
        sniffer.start()
        client.loop_forever()

    # On message / On connect / On disconnect
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.subscribe(mqttSubTopic, 2)

def on_connect(client, userdata, flags, rc):
     """
     Connection to the broker
     """
     if rc == 0:
        #logger.info("Connected to broker %s:%d" % (client.host, client.port))
        logger.info("Connected to broker. Return code: %d" % rc)
     else:
        logger.warning("An error occured on connect. Return code: %d " % rc)
        clean()

def on_disconnect(client, userdata, rc):
     """
     Triggers when the client is disconnected
     """
     if rc == 0:
        logger.info("Client successfully disconnected")
     else:
        logger.info("Something was wrong. Return code %s. Reconnecting" % rc)
        time.sleep(5)
        connect()

def on_message(client, userdata, message):
    """
    A message has been published to /rpi/rf433/in topic.
    The payload is supposed to contain the RF 433 code to send
    """
    logger.log(logging.DEBUG, "Message [%s] from topic [%s]" % (message.payload, message.topic))
    logger.log(logging.DEBUG, "Sending RF433 code [%s]" % message.payload)

def main(argv):
    """
    Main
    """
    # Logging level
    # CRITICAL = 50, ERROR = 40, WARNING = 30, INFO = 20, DEBUG = 10, NOTSET = 0
    logLevel = logging.DEBUG # default value

    global mqttHost
    global mqttPort
    global mqttSubTopic
    global mqttPubTopic
    recvPin   = int(os.getenv('recvPin', '24'))
    sendPin   = int(os.getenv('sendPin', '24'))
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)

    # Checks the optional parameters
    try:
        opts, args = getopt.getopt(argv, "hr:s:H:p:P:S:l:",
                     ["help","receive-pin=","send-pin=","mqtt-host=","mqtt-port=","publish-topic=","subscribe-topic=","log-level="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-r", "--receive-pin" ):
            recvPin = int(a)
        if o in ("-s", "--send-pin" ):
            sendPin = int(a)
        if o in ("-P", "--publish-topic" ):
            pubTopic = a
        if o in ("-S", "--subscribe-topic" ):
            subTopic = a
        if o in ("-l", "--log-level" ):
            logLevel = int(a)
        if o in ("-H", "--mqtt-host" ):
            mqttHost = a
        if o in ("-p", "--mqtt-port" ):
            mqttPort = int(a)

    # Intercept signals
    signal.signal(signal.SIGTERM, clean)
    signal.signal(signal.SIGINT, clean)

    logger.setLevel(logLevel)

    print "*** RPi MQTT to RF433 gateway ***"
    print " - Receive pin (wiringPi) : %d" % recvPin
    print " - Send pin (wiringPi)    : %d" % sendPin
    print " - MQTT broker host       : %s" % mqttHost
    print " - MQTT broker port       : %d" % mqttPort
    print " - Publish to topic       : %s" % mqttPubTopic
    print " - Subscribe to topic     : %s" % mqttSubTopic

    connect()
    sniffer = RFSniffer(client, mqttPubTopic, logLevel)
    sniffer.start()
    client.loop_forever()

if __name__ == "__main__":
    main(sys.argv[1:])
