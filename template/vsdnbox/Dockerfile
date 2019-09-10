FROM fedora:latest
RUN dnf update -y

RUN dnf install -y openvswitch wget git util-linux net-tools gcc procps nano iputils hostname

RUN dnf install -y snappy-devel python3-devel libyaml-devel openvswitch-devel

RUN mkdir /code
WORKDIR /code
RUN git clone https://github.com/fernnf/vsdnagent.git
WORKDIR /code/vsdnagent

RUN pip3 install -r requirements.txt
COPY vsdnagent.sh .
RUN chmod +x vsdnagent.sh

WORKDIR /root
RUN git clone https://github.com/fernnf/benchtraffic.git
RUN pip3 install -r benchtraffic/requirements.txt

RUN mkdir /root/results


WORKDIR /code/vsdnagent

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

CMD ["/bin/bash", "vsdnagent.sh"]
