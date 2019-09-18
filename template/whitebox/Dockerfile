FROM alpine:latest
RUN apk update 
RUN apk --update add openvswitch util-linux net-tools nano iputils python3 py3-pip openssl ca-certificates git bash
RUN apk --update add --virtual build-dependencies python3-dev build-base wget libffi-dev openssl-dev linux-headers snappy-dev
WORKDIR /bin
COPY boot.sh .
RUN chmod +x boot.sh

WORKDIR /root

RUN git clone https://github.com/fernnf/benchtraffic.git

RUN pip3 install --upgrade pip && pip3 install -r benchtraffic/requirements.txt


WORKDIR /

ENV PS1="[vsdn:whitebox \u@\h]# "

LABEL br.ufpa.label.name="WhiteBox"\
      br.ufpa.label.description="Whitebox Switch"\
      br.ufpa.label.vendor="Federal University of Para"\
      br.ufpa.label.contact="fernnf@gmail.com"\
      br.ufpa.label.application="vSDNAgent"\
      br.ufpa.label.version="0.1"\
      br.ufpa.label.license="Apache2"

RUN  apk del build-dependencies

ENTRYPOINT [ "/bin/sh" ]

CMD ["/bin/boot.sh"]
