# Build:
#   docker build -t ksahnine/rpi-mqtt-rf433 .
#
# Run:
#   docker run --privileged -td ksahnine/rpi-mqtt-rf433
#
# DOCKER_VERSION 1.6

# Base image
FROM ksahnine/rpi-python-stack
MAINTAINER Kadda SAHNINE <ksahnine@gmail.com>

ENV RECV_PIN 2
ENV SEND_PIN 0
ENV HOST localhost
ENV MQTT_PORT 1883
ENV MQTT_SUB_TOPIC /rpi/rf433/in
ENV MQTT_PUB_TOPIC /rpi/rf433/out

# Install wiringpi2
RUN mkdir /var/wp2 && cd /var/wp2 && \
    git config --global http.sslVerify false && \
    git clone git://git.drogon.net/wiringPi && \
    git clone https://github.com/Gadgetoid/WiringPi2-Python.git && \
    cd /var/wp2/wiringPi && ./build && \
    cd /var/wp2/WiringPi2-Python && python setup.py install

# Install 433Utils (fork)
RUN mkdir /root/rf433 && cd /root/rf433 && \
    wget --no-check-certificate https://github.com/ksahnine/433Utils/archive/master.zip && \
    unzip master.zip && cd 433Utils-master/RPi_utils && \
    make install && rm -rf /root/rf433

# Add custom program
COPY src/rf2mqtt.py /app/rf2mqtt.py
COPY src/libs/__init__.py /app/libs/__init__.py
COPY src/libs/rfsniffer.py /app/libs/rfsniffer.py

# Define working directory
WORKDIR /app

# Bootstrap
ENTRYPOINT [ "python", "/app/rf2mqtt.py" ]
