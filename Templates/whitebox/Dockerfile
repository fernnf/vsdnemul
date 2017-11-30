FROM fedora:latest

RUN dnf -y update &&  dnf install -y openvswitch hostname iputils iproute tcpdump nano net-tools

VOLUME /etc/openvswitch/

RUN mkdir /trace

EXPOSE 6640 6653 6633

ADD boot.sh /bin/boot.sh

CMD /bin/sh /bin/boot.sh
