FROM centos:6.10

RUN yum update -y && yum install wget sudo nano -y

WORKDIR /root

RUN wget http://updates.onlab.us/GPG-KEY-ONLAB

RUN rpm --import GPG-KEY-ONLAB

RUN echo -e "[onlab] \nname=ON.Lab Software Releases \nbaseurl=http://updates.onlab.us/rpm/stable \nenabled=1 \ngpgcheck=1" >> /etc/yum.repos.d/onlab.repo

RUN yum update -y

RUN yum install flowvisor -y

RUN fvconfig generate /etc/flowvisor/config.json flowvisor flowvisor

RUN sed -i 's/"run_topology_server": false/"run_topology_server": true/' /etc/flowvisor/config.json

RUN fvconfig load /etc/flowvisor/config.json

RUN sed -i -e "s/\/sbin\/flowvisor /\/sbin\/flowvisor -l /ig" /etc/init.d/flowvisor

ENV TERM=vt100

ENV HOME /root

ENV BUILD_NUMBER docker

ENV PS1="[vsdn:host \u@\h]# "

LABEL br.ufpa.label.name="FlowVisor"\
      br.ufpa.label.description="Hypervisor SDN"\
      br.ufpa.label.vendor="Federal University of Para"\
      br.ufpa.label.contact="fernnf@gmail.com"\
      br.ufpa.label.application="vSDNAgent"\
      br.ufpa.label.version="0.2"\
      br.ufpa.label.license="Apache2"

WORKDIR /bin

RUN wget https://raw.githubusercontent.com/fernnf/vsdnemul/master/template/flowvisor/boot.sh

WORKDIR /

ENTRYPOINT [ "/bin/sh" ]

CMD ["/bin/boot.sh"]
