FROM alpine:latest

RUN apk update

RUN apk add openjdk7 git bash nano python

ENV JAVA_HOME=/usr/lib/jvm/java-1.7-openjdk

RUN wget http://mirror.nbtelecom.com.br/apache/maven/maven-3/3.6.0/binaries/apache-maven-3.6.0-bin.tar.gz

RUN tar -xvzf apache-maven-3.6.0-bin.tar.gz && mv apache-maven-3.6.0 maven

RUN wget https://github.com/fernnf/vsdnemul/blob/master/template/openvirtex/openvirtex.tar.gz?raw=true -O openvirtex.tar.gz

RUN tar -xvzf openvirtex.tar.gz

RUN chmod +x /openvertix/utils/ovxctl.py && ln -s /openvertix/utils/ovxctl.py /usr/bin/ovxctl

LABEL br.ufpa.label.name="OpenVirteX"\
      br.ufpa.label.description="Hypervisor SDN"\
      br.ufpa.label.vendor="Federal University of Para"\
      br.ufpa.label.contact="fernnf@gmail.com"\
      br.ufpa.label.application="vSDNAgent"\
      br.ufpa.label.version="0.2"\
      br.ufpa.label.license="Apache2"

ENTRYPOINT ["/bin/sh"]

CMD ["/openvertix/scripts/ovx.sh"]

