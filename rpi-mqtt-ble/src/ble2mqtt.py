#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__  = "Kadda SAHNINE"
__contact__ = "ksahnine@gmail.com"
__license__ = 'GPL v3'

import bluetooth
import getopt
import logging
import os
import paho.mqtt.client as mqtt
import sys
import time
import yaml

def usage():
    """
    Display usage
    """
    sys.stderr.write( "Usage: ble2mqtt.py [-c <config-file> | --config=<config-file>\n"+
          "                   [-h <mqtt-host>   | --mqtt-host=<mqtt-host>\n"+
          "                   [-p <mqtt-port>   | --mqtt-port=<mqtt-port>\n")

def publish(client, mqttHost, mqttPort, device, data, logger):
    """
    Publish a MQTT message to the topic dedicated to the device visibility
    """
    topic = "/gateway/ble/"+device+"/visibility"
    logger.log(logging.DEBUG, "Connecting to MQTT broker [%s:%d]" % (mqttHost, mqttPort))
    client.connect(mqttHost, mqttPort, 5)
    client.publish(topic, data)
    logger.log(logging.DEBUG, "Publishing [%s] to topic [%s]" % (data, topic))
    client.disconnect()

def main(argv):
    """
    Main
    """
    configFile = "/config/devices.yml"
    mqttHost = os.getenv('MQTT_HOST', 'localhost')
    mqttPort = int(os.getenv('MQTT_PORT', '1883'))
    mqttTopic = os.getenv('MQTT_TOPIC', '/gateway/ble')
    client = mqtt.Client()
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)

    # Checks the optional parameters
    try:
        opts, args = getopt.getopt(argv, "hH:p:c:",
                     ["help","mqtt-host=","mqtt-port=","config"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-H", "--mqtt-host" ):
            mqttHost = a
        if o in ("-p", "--mqtt-port" ):
            mqttPort = int(a)
        if o in ("-c", "--config" ):
            configFile = a

    # Loads the configuration file
    if os.path.isfile(configFile):
        with open(configFile, 'r') as f:
            conf = yaml.load(f)
    else:
        print "ERROR. The config file [%s] does not exist !" % configFile
        usage()
        sys.exit(3)
    
    # Configure the logger
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.setLevel(conf['logging_level'])
    logger.addHandler(handler)

    delay = int(conf["delay"])
    timeout = int(conf["timeout"])
    
    print "*** BLE to MQTT gateway ***"
    print " - Devices config file : %s" % configFile
    print " - MQTT host           : %s" % mqttHost
    print " - MQTT port           : %d" % mqttPort
    print " - Publish to topic    : /gateway/ble/<device>/visibility"
    
    lastResults = dict()
    while True:
        for device, bdaddr in conf["devices"].iteritems():
            result = bluetooth.lookup_name(bdaddr, timeout=timeout)
            if (result != None):
                if not (device in lastResults) or ((device in lastResults) and result != lastResults[device]):
       	            logger.log(logging.DEBUG, "%s: in" % device)
                    publish(client, mqttHost, mqttPort, device, "in", logger)
            else:
                if not (device in lastResults) or ((device in lastResults) and result != lastResults[device]):
       	            logger.log(logging.DEBUG, "%s: out" % device)
                    publish(client, mqttHost, mqttPort, device, "out", logger)
    
            lastResults[device]=result
        
        time.sleep(delay)

if __name__ == "__main__":
    main(sys.argv[1:])
