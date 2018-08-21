FROM alpine:edge
RUN apk update
RUN apk add iperf3 tcpdump iputils nano ethtool iproute2 net-tools bash

ENV TERM=vt100
ENV PS1="[vsdn:host \u@\h]# "

LABEL br.ufpa.label.name="Host"\
      br.ufpa.label.description="Host computer"\
      br.ufpa.label.vendor="Federal University of Para"\
      br.ufpa.label.contact="fernnf@gmail.com"\
      br.ufpa.label.application="vSDNAgent"\
      br.ufpa.label.version="0.1"\
      br.ufpa.label.license="Apache2"

CMD [ "/bin/ash" ] 

