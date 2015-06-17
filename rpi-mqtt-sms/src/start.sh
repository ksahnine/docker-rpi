#!/bin/sh
########################
# starts.sh

# Starts the SMS gateway daemon
gammu-smsd -c $GAMMU_CONFIG -d
RC=$?
if [ $RC -eq 0 ]
then
    # Starts the SMS to MQTT gateway
    python mqtt2sms.py $@
    RC=$?
fi

# Kill gammu daemon
echo "Shutting down gammu-smsd"
killall -9 gammu-smsd

return $RC
