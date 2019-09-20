FROM ubuntu:latest

# Author
MAINTAINER  Docker INS <docker@ins.hsr.ch>

# Update the apt information
# Install python
# Install wget
# Download osrg/ryu/archive/master.zip
# Install (unzip) ryu
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3-setuptools \
      python3-pip \
      python3-eventlet \
      python3-lxml \
      wget \
      unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install ryu


# 6633 - OpenFlow
EXPOSE 6653


# Define working directory.
WORKDIR /opt/ryu


# Define default command.
CMD ["ryu-manager", "ryu.app.simple_switch"]