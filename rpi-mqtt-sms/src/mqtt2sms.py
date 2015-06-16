# /usr/bin/python
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
import subprocess
import time

client = mqtt.Client()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
mqttHost = os.getenv('MQTT_HOST', 'localhost')
mqttPort = int(os.getenv('MQTT_PORT', '1883'))
mqttSubTopic = os.getenv('MQTT_SUB_TOPIC', '/rpi/sms/in/+') # MQTT to SMS topic
sendSmsProgram = os.getenv('SEND_SMS_PROGRAM', '/app/send_sms.sh') 
gammuConfig = os.getenv('GAMMU_CONFIG', '/config/gammu-smsdrc') 

def usage():
    """
    Display usage
    """
    sys.stderr.write( "Usage: rf2mqtt.py [-t <topic>       | --topic=<mqtt_to_sms_topic>\n"+
          "                   [-H <mqtt-host>   | --mqtt-host=<mqtt-host>\n"+
          "                   [-p <mqtt-port>   | --mqtt-port=<mqtt-port>\n"+
          "                   [-G <gammu-conf>  | --gammu-config=<gammu-conf>\n"+
          "                   [-P <sms-prog>    | --send-sms-prog=<sms-prog>\n"+
          "                   [-l <logLevel>    | --log-level=<logLevel>\n")

def hasRootPrivilege():
    if os.getuid() == 0:
        return True
    else:
        return False

def clean(signum, frame):
     """
     Signal handler (SIGTERM / SIGINT)
     """
     logger.info("Disconnecting from the broker")
     client.disconnect()
     stopGammu()
     sys.exit(signum)

def startGammu():
    cmdLine = [ "gammu-smsd", "-c", gammuConfig, "-d" ]
    rc = subprocess.call(cmdLine)
    if rc != 0:
        logger.warning("Failed to start Gammu. Error code %d" % rc)
    else:
        logger.info("Gammu daemon started")

def stopGammu():
    cmdLine = [ "killall", "-9", "gammu-smsd" ]
    rc = subprocess.call(cmdLine)
    if rc != 0:
        logger.warning("Failed to stop Gammu. Error code %d" % rc)
    else:
        logger.info("Gammu daemon stopped")

def sendSMS(to, text):
    cmdLine = [ sendSmsProgram, to, text, gammuConfig ]
    rc = subprocess.call(cmdLine)
    if rc != 0:
        logger.warning("Failed to send the sms. Error code %d" % rc)
    else:
        logger.info("SMS sent")

def connect():
    """
    Connect to the MQTT broker and subscribe to topic
    """
    rc = client.connect(mqttHost, mqttPort, 60)
    if rc != 0:
        logger.info("Connection failed with error code %s. Retrying", result)
        time.sleep(10)
        connect()
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
    A message has been published to /rpi/sms/in/<phone_number> topic.
    The payload is supposed to contain the message to send
    """
    logger.log(logging.DEBUG, "Message [%s] from topic [%s]" % (message.payload, message.topic))
    sendSmsTo = message.topic.rsplit('/', 1)[1]
    logger.log(logging.DEBUG, "Trying to send the SMS to [%s]" % sendSmsTo)
    sendSMS(sendSmsTo, message.payload)

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
    global sendSmsProgram
    global gammuConfig
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)

    # Checks the optional parameters
    try:
        opts, args = getopt.getopt(argv, "hH:p:t:G:P:l:",
                     ["help","mqtt-host=","mqtt-port=","topic=","gammu-config=","send-sms-program=","log-level="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-t", "--topic" ):
            pubTopic = a
        if o in ("-l", "--log-level" ):
            logLevel = int(a)
        if o in ("-H", "--mqtt-host" ):
            mqttHost = a
        if o in ("-p", "--mqtt-port" ):
            mqttPort = int(a)
        if o in ("-G", "--gammu-config" ):
            gammuConfig = a
        if o in ("-P", "--send-sms-program" ):
            sendSmsProgram = a

    logger.setLevel(logLevel)

    # Checks if the current user has root privileges
    if not hasRootPrivilege():
        logger.error("The current user must have root privileges. Please, use sudo.")
        sys.exit(0)
        
    # Intercept signals
    signal.signal(signal.SIGTERM, clean)
    signal.signal(signal.SIGINT, clean)

    print "*** RPi MQTT to SMS gateway ***"
    print " - MQTT broker host       : %s" % mqttHost
    print " - MQTT broker port       : %d" % mqttPort
    print " - Subscribe to topic     : %s" % mqttSubTopic
    print " - Gammu config file      : %s" % gammuConfig
    print " - Send SMS program       : %s" % sendSmsProgram

    connect()
    startGammu()
    client.loop_forever()

if __name__ == "__main__":
    main(sys.argv[1:])
