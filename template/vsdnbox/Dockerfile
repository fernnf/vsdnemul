FROM fedora:latest
RUN dnf update -y

RUN dnf install -y openvswitch wget supervisor git util-linux net-tools gcc procps

RUN dnf install -y snappy-devel python3-devel libyaml-devel openvswitch-devel

RUN mkdir /code
WORKDIR /code
RUN git clone https://github.com/fernnf/vsdnagent.git
WORKDIR /code/vsdnagent

RUN pip3 install -r requirements.txt
WORKDIR /etc
COPY supervisord.conf .
WORKDIR /
COPY ovsdb.sh .
RUN chmod +x ovsdb.sh

COPY vsdnagent.sh .
RUN chmod +x vsdnagent.sh

ENV PS1="[vsdn:vsdnbox \u@\h]#"
ENV ORCH_REALM="realm1"
ENV OVS_ADDR="tcp:127.0.0.1:6640"
ENV ORCH_TRANS_BRIDGE="tswitch0"

LABEL br.ufpa.label.name="VSDNBox"\
      br.ufpa.label.description="Whitebox Switch with vSDNAgent"\
      br.ufpa.label.vendor="Federal University of Para"\
      br.ufpa.label.contact="fernnf@gmail.com"\
      br.ufpa.label.application="vSDNagent"\
      br.ufpa.label.version="0.1"\
      br.ufpa.label.license="Apache2"

RUN dnf clean all

CMD "/usr/bin/supervisord"
#CMD "/usr/bin/supervisord"
