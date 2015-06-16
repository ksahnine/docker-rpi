import threading 
import logging 
import subprocess 
import time 
import paho.mqtt.client as mqtt
  
class RFSniffer(threading.Thread): 
    def __init__(self, mqttClient, mqttTopic = '/rpi/rf433/out', logLevel = logging.DEBUG): 
        threading.Thread.__init__(self) 
        self.daemon = True 
        self.client = mqttClient 
        self.mqttTopic = mqttTopic 
        self._stopevent = threading.Event() 
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()
        self.logger.setLevel(logLevel)
    def run(self): 
        i = 0 
        while not self._stopevent.isSet(): 
            proc = subprocess.Popen(["sudo", "/usr/local/bin/RFSniffer"],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
            for line in iter(proc.stdout.readline,''):
                # The RF receiver has received an incoming signal.
                rfcode = line.rstrip()
                self.client.publish(self.mqttTopic, rfcode)
                self.logger.log(logging.DEBUG, "Publishing [%s] to topic [%s]" % (rfcode, self.mqttTopic))
    def stop(self): 
        self._stopevent.set()
