FROM fedora:27

RUN dnf -y update 

RUN dnf -y install openvswitch tcpdump nano net-tools iproute ethtool

RUN dnf -y clean all

COPY boot.sh /bin/boot.sh

CMD /bin/sh /bin/boot.sh

#RUN dnf -y update &&  dnf install -y openvswitch hostname iputils iproute tcpdump nano net-tools

#VOLUME /etc/openvswitch/

#RUN mkdir /trace

#EXPOSE 6640 6653 6633

#ADD boot.sh /bin/boot.sh

#CMD /bin/sh /bin/boot.sh
