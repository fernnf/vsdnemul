FROM debian:wheezy

RUN apt-get update -y

RUN apt-get install wget -y

RUN wget -q http://updates.onlab.us/GPG-KEY-ONLAB -O- | apt-key add -

RUN sh -c "echo 'deb http://updates.onlab.us/debian stable/' > /etc/apt/sources.list.d/flowvisor.list"

RUN apt-get update -y && apt-get install flowvisor=0.8.17-3 -y

RUN fvconfig generate /etc/flowvisor/config.json localhost 123456

RUN sed -i 's/"run_topology_server": false/"run_topology_server": true/' /etc/flowvisor/config.json

RUN fvconfig load /etc/flowvisor/config.json

RUN sed -i -e "s/\/sbin\/flowvisor /\/sbin\/flowvisor -l /ig" /etc/init.d/flowvisor

ENV TERM=vt100
ENV PS1="[vsdn:host \u@\h]# "

LABEL br.ufpa.label.name="FlowVisor"\
      br.ufpa.label.description="Hypervisor SDN"\
      br.ufpa.label.vendor="Federal University of Para"\
      br.ufpa.label.contact="fernnf@gmail.com"\
      br.ufpa.label.application="vSDNAgent"\
      br.ufpa.label.version="0.2"\
      br.ufpa.label.license="Apache2"

