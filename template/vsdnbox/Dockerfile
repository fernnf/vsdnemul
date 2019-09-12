FROM alpine:latest

RUN apk --update add openvswitch util-linux net-tools nano iputils python3 py3-pip openssl ca-certificates git bash

RUN apk --update add --virtual build-dependencies python3-dev build-base wget libffi-dev openssl-dev


RUN mkdir /code
WORKDIR /code
RUN git clone https://github.com/fernnf/vsdnagent.git
WORKDIR /code/vsdnagent

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY vsdnagent.sh .

RUN chmod +x vsdnagent.sh

WORKDIR /root

RUN git clone https://github.com/fernnf/benchtraffic.git

RUN pip3 install -r benchtraffic/requirements.txt

RUN  apk del build-dependencies

WORKDIR /code/vsdnagent

RUN mkdir /root/results

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

CMD ["/bin/bash", "vsdnagent.sh"]