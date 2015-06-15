# Build:
#   docker build -t ksahnine/rpi-mqtt-pir .
#
# Run:
#   docker run -d --privileged ksahnine/rpi-mqtt-pir
#
# DOCKER_VERSION 1.6

# Base image
FROM ksahnine/rpi-python-stack
MAINTAINER Kadda SAHNINE <ksahnine@gmail.com>

ENV pirPin 24
ENV delay 60
ENV MQTT_HOST 192.168.0.22
ENV MQTT_PORT 1883
ENV MQTT_TOPIC /rpi/sensors/pir
ENV MQTT_MESSAGE true

# Install Python RPi GPIO
RUN pip install rpi.gpio

# Install MQTT libraries
RUN pip install paho-mqtt

# Add custom program
COPY src/motion_notifier.py /app/motion_notifier.py

# Define working directory
WORKDIR /app

# Define default command
ENTRYPOINT ["python", "motion_notifier.py"]
