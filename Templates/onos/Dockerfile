FROM fedora:27
LABEL maintainer="fernnf@gmail.com"
LABEL project="vSDNAgent SDN Environment prototyper"
LABEL Name="ONOS Controller image"
LABEL Version="0.1"

WORKDIR /root

RUN dnf -y update 

RUN dnf -y install nano wget net-tools iputils

RUN wget --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/8u151-b12/e758a0de34e24606bca991d704f6dcbf/jdk-8u151-linux-x64.rpm"

RUN dnf install -y jdk-8u151-linux-x64.rpm

RUN echo "JAVA_HOME=/usr/java/latest" >> /etc/environment
RUN echo "JRE_HOME=/usr/java/latest/jre" >> /etc/environment
RUN echo "PATH=${PATH}:/${JAVA_HOME}/bin:${JRE_HOME}/bin" >> /etc/environment

ENV JAVA_HOME=/usr/java/latest
ENV JRE_HOME=/usr/java/latest/jre
ENV PATH=${PATH}:${JAVA_HOME}/bin:${JRE_HOME}/bin

WORKDIR /opt
RUN wget -c http://onlab.vicci.org/onos/release/onos-1.12.0.tar.gz
RUN dnf -y install tar 
RUN tar -xvzf onos-1.12.0.tar.gz && mv onos-1.12.0 onos
RUN cp /opt/onos/init/onos.initd /etc/init.d/onos
RUN cp /opt/onos/init/onos.conf /etc/init.d/onos.conf
RUN cp /opt/onos/init/onos.service /etc/systemd/system/

RUN systemctl enable onos 

RUN sed -i "s/SYS_APPS=drivers/SYS_APPS=drivers,openflow,fwd,proxyarp,ovsdb/" /opt/onos/bin/onos-service

RUN dnf clean all

EXPOSE 6653 6640 8181 8101 9876

CMD [ "/usr/sbin/init" ]

#CMD [ "/bin/bash"]

