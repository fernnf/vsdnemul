FROM onosproject/onos
RUN apk update
RUN apk add bash tcpdump
ENV PS1="[vsdn:onos \u@\h]# "
RUN sed -i "s/SYS_APPS=drivers/SYS_APPS=drivers,openflow,fwd,proxyarp,ovsdb/" /root/onos/bin/onos-service

LABEL br.ufpa.label.name="ONOS"\
      br.ufpa.label.description="Network Controller Computer"\
      br.ufpa.label.vendor="Federal University of Para"\
      br.ufpa.label.contact="fernnf@gmail.com"\
      br.ufpa.label.application="vSDNAgent"\
      br.ufpa.label.version="0.1"\
      br.ufpa.label.license="Apache2"
WORKDIR /root/onos
ENTRYPOINT ["./bin/onos-service"]
CMD ["server"]
