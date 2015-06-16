#!/bin/sh
########################
# send_sms.sh <phone_num> <message>

GAMMU_CONFIG=./conf/gammu-smsdrc

PhonNum=$1
Message=$2
GammuConfig=$3

Here=`dirname $0`

if [ -z $PinCode ]
then
    PinCode=$4
fi

if [ $# -lt 3 ]
then
    echo "Usage : send_sms.sh <phone_num> <message> <gammuConfigFile>"
    exit 4
fi

# Ready to send the SMS
echo "$Message" | gammu-smsd-inject -c $GammuConfig TEXT $PhonNum
RC=$?
if [ $RC -eq 0 ]
then
    echo "Message sent"
    exit 0
else
    echo "ERROR. Unable to send the SMS. Return code : $RC"
    exit 1
fi
