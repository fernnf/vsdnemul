FROM alpine:latest
RUN apk update 
RUN apk add --upgrade busybox 
RUN apk add openvswitch tcpdump nano iproute2 ethtool bash util-linux wget
WORKDIR /bin
RUN wget https://raw.githubusercontent.com/fernnf/vsdnemul/master/template/whitebox/boot.sh

# COPY template/whitebox/boot.sh /bin/boot.sh
WORKDIR /

ENV PS1="[vsdn:whitebox \u@\h]# "

LABEL br.ufpa.label.name="WhiteBox"\
      br.ufpa.label.description="Whitebox Switch"\
      br.ufpa.label.vendor="Federal University of Para"\
      br.ufpa.label.contact="fernnf@gmail.com"\
      br.ufpa.label.application="vSDNAgent"\
      br.ufpa.label.version="0.1"\
      br.ufpa.label.license="Apache2"


ENTRYPOINT [ "/bin/sh" ]

CMD ["/bin/boot.sh"]
