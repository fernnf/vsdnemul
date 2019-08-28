FROM ubuntu:latest
RUN apt update

RUN apt install -y openvswitch-switch wget supervisor git python3 python3-pip libsnappy-dev util-linux
#RUN apk add openvswitch tcpdump nano iproute2 ethtool bash util-linux wget supervisor git gcc musl-dev libc-dev libffi-dev

RUN mkdir /code

WORKDIR /code

RUN git clone https://github.com/fernnf/vsdnagent.git

WORKDIR /code/vsdnagent

RUN pip3 install --requirement requirements.txt

RUN python3 setup.py install

WORKDIR /etc

COPY supervisord.conf .

WORKDIR /

COPY boot.sh .

RUN chmod +x boot.sh

ENV PS1="[vsdn:vsdnbox \u@\h]#"
ENV ORCH_REALM="realm1"
ENV OVS_ADDR="tcp:127.0.0.1:6640"
ENV ORCH_TRANS_BRIDGE="tswitch0"
ENV PYTHONLIBS=.

LABEL br.ufpa.label.name="VSDNBox"\
      br.ufpa.label.description="Whitebox Switch with vSDNAgent"\
      br.ufpa.label.vendor="Federal University of Para"\
      br.ufpa.label.contact="fernnf@gmail.com"\
      br.ufpa.label.application="vSDNagent"\
      br.ufpa.label.version="0.1"\
      br.ufpa.label.license="Apache2"

CMD "/usr/bin/supervisord"
#CMD "/bin/bash"