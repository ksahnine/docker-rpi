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
import sys
import time

def usage():
    """
    Display usage
    """
    sys.stderr.write( "Usage: motion_notifier.py [-P <pir-pin> | --pir-pin=<pir-pin>\n"+
          "                   [-d <delay>       | --delay=<delay>\n"+
          "                   [-t <topic>       | --topic=<topic>\n"+
          "                   [-m <message>     | --message=<message>\n"+
          "                   [-l <logLevel>    | --log-level=<logLevel>\n"+
          "                   [-h <mqtt-host>   | --mqtt-host=<mqtt-host>\n"+
          "                   [-p <mqtt-port>   | --mqtt-port=<mqtt-port>\n")

def publish(client, mqttHost, mqttPort, mqttTopic, mqttMessage, logger):
    """
    Publish a MQTT message to the given topic parameter when a move is detected
    """
    logger.log(logging.DEBUG, "Connecting to MQTT broker [%s:%d]" % (mqttHost, mqttPort))
    client.connect(mqttHost, mqttPort, 5)
    client.publish(mqttTopic, mqttMessage)
    logger.log(logging.DEBUG, "Publishing [%s] to topic [%s]" % (mqttMessage, mqttTopic))
    client.disconnect()

def main(argv):
    """
    Main
    """
    # Logging level
    # CRITICAL = 50, ERROR = 40, WARNING = 30, INFO = 20, DEBUG = 10, NOTSET = 0
    logLevel = logging.DEBUG # default value

    pirPin   = int(os.getenv('pirPin', '24'))
    delay    = int(os.getenv('delay', '60')) # one minute between 2 notifications
    mqttHost = os.getenv('MQTT_HOST', 'localhost')
    mqttPort = int(os.getenv('MQTT_PORT', '1883'))
    mqttTopic = os.getenv('MQTT_TOPIC', '/rpi/sensors/pir')
    mqttMessage = os.getenv('MQTT_MESSAGE', 'true')
    client = mqtt.Client()
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)

    # Checks the optional parameters
    try:
        opts, args = getopt.getopt(argv, "hP:d:H:p:t:m:l:",
                     ["help","pir-pin=","delay=","mqtt-host=","mqtt-port=","topic=","message=","log-level="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-P", "--pir-pin" ):
            pirPin = int(a)
        if o in ("-d", "--delay" ):
            delay = int(a)
        if o in ("-l", "--log-level" ):
            logLevel = int(a)
        if o in ("-H", "--mqtt-host" ):
            mqttHost = a
        if o in ("-p", "--mqtt-port" ):
            mqttPort = int(a)
        if o in ("-t", "--topic" ):
            configFile = a
        if o in ("-m", "--message" ):
            mqttMessage = a

    io.setmode(io.BCM)
    io.setup(pirPin, io.IN)         # Entree du signal du capteur PIR
    
    # Configure the logger
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.setLevel(logLevel)
    logger.addHandler(handler)

    print "*** RPi PIR sensor ***"
    print " - PIR pin (BCM)       : %d" % pirPin
    print " - Delay btw 2 notif   : %d seconds" % delay
    print " - MQTT broker host    : %s" % mqttHost
    print " - MQTT broker port    : %d" % mqttPort
    print " - Publish to topic    : %s" % mqttTopic
    print " - Message to publish  : %s" % mqttMessage

    last_time = 0
    while True:
        if io.input(pirPin):
            logger.log(logging.DEBUG, "Mouvement detecte")
            detection_time = time.time()
            if (detection_time-last_time > delay):
                logger.log(logging.DEBUG, "Notification du mouvement")
                # Notification de presence
                publish(client, mqttHost, mqttPort, mqttTopic, mqttMessage, logger)
    
            last_time = detection_time
        time.sleep(0.5)

if __name__ == "__main__":
    main(sys.argv[1:])
