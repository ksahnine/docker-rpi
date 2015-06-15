# Build:
#   docker build -t ksahnine/rpi-mqtt-ble .
#
# Run:
#   docker run -d ksahnine/rpi-mqtt-ble
#
# DOCKER_VERSION 1.6

# Base image
FROM ksahnine/rpi-python-stack
MAINTAINER Kadda SAHNINE <ksahnine@gmail.com>

ENV MQTT_HOST 192.168.0.22
ENV MQTT_PORT 1883

# Install dependencies
RUN apt-get update && apt-get install -y \
    python-yaml \
    bluetooth \
    python-bluetooth \
    --no-install-recommends

# Install MQTT libraries
RUN pip install paho-mqtt

# Add custom program
COPY src/ble2mqtt.py /app/ble2mqtt.py

# Define working directory
WORKDIR /app

# Define default command
#ENTRYPOINT ["python", "/app/ble2mqtt.py"]

# Display usage
#CMD ["-h"]
