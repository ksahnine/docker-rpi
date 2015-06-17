#!/bin/sh
###############################
# sms2mqtt.sh

env > /tmp/sms2mqtt.log
echo $@ >> /tmp/sms2mqtt.log
# This shell is triggered on a incomming SMS
# It publishes the SMS message to the given topic parameter
MQTT_HOST=$1
MQTT_PORT=$2
MQTT_PUB_TOPIC=$3
INBOX=/var/spool/gammu/inbox

RC=0
for ID in "$@" ; do
    mosquitto_pub -h $MQTT_HOST -p MQTT_PORT -t $MQTT_TOPIC -m "`cat $INBOX/$ID`"
    if [ $RC -ne 0 ]
    then
        RC=$?
    fi
done

exit $RC
