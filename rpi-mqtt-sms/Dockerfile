# Build:
#   docker build -t ksahnine/rpi-sms-daemon .
#
# Run:
#   docker run -td -p 80:5000 ksahnine/rpi-sms-daemon
#
# DOCKER_VERSION 1.6

# Base image
FROM ksahnine/rpi-python-stack
MAINTAINER Kadda SAHNINE <ksahnine@gmail.com>

ENV MQTT_HOST localhost
ENV MQTT_PORT 1883
ENV MQTT_SUB_TOPIC /rpi/sms/in/+
ENV MQTT_PUB_TOPIC /rpi/sms/out
ENV SEND_SMS_PROGRAM /app/send_sms.sh
ENV GAMMU_CONFIG /config/gammu-smsdrc

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    usb-modeswitch \
    gammu-smsd \
    mosquitto-client \
    --no-install-recommends

# Install Python RPi GPIO
RUN pip install rpi.gpio

# Install MQTT client lib
RUN pip install paho-mqtt

# Add custom program
COPY src/start.sh /app/start.sh
COPY src/mqtt2sms.py /app/mqtt2sms.py
COPY src/send_sms.sh /app/send_sms.sh
COPY src/sms2mqtt.sh /app/sms2mqtt.sh
COPY src/conf/gammu-smsdrc /config/gammu-smsdrc

# Define working directory
WORKDIR /app

# Starts the service
ENTRYPOINT ["/app/start.sh" ]
