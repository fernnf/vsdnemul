FROM alpine:latest

RUN apk update

RUN apk add openjdk7 git bash nano python mongodb

ENV JAVA_HOME=/usr/lib/jvm/java-1.7-openjdk

RUN wget http://mirror.nbtelecom.com.br/apache/maven/maven-3/3.6.0/binaries/apache-maven-3.6.0-bin.tar.gz

RUN wget https://github.com/fernnf/vsdnemul/blob/master/template/openvirtex/openvirtex.tar.gz?raw=true -O openvirtex.tar.gz

RUN tar -xvzf openvirtex.tar.gz

RUN chmod +x /openvirtex/utils/ovxctl.py && ln -s /openvirtex/utils/ovxctl.py /usr/bin/ovxctl

RUN apk add supervisor

RUN mkdir -p /data/db

RUN echo $'[unix_http_server] \n\
file=/run/supervisord.sock \n\
\n\
[supervisord] \n\
logfile=/var/log/supervisord.log \n\
loglevel=info \n\
nodaemon=true \n\
\n\
[rpcinterface:supervisor] \n\
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface \n\
\n\
[supervisorctl] \n\
serverurl=unix:///var/run/supervisord.sock \n\
\n\
[program:mongod] \n\
command=/usr/bin/mongod --bind_ip 0.0.0.0 \n\
\n\
[program:openvirtex] \n\
command=/openvirtex/scripts/ovx.sh \n'\
> /etc/supervisord.conf

RUN cat /etc/supervisord.conf

ENV PS1="[vsdn:hypervisor  \u@\h]# "

LABEL br.ufpa.label.name="OpenVirteX"\
      br.ufpa.label.description="Hypervisor SDN"\
      br.ufpa.label.vendor="Federal University of Para"\
      br.ufpa.label.contact="fernnf@gmail.com"\
      br.ufpa.label.application="vSDNAgent"\
      br.ufpa.label.version="0.2"\
      br.ufpa.label.license="Apache2"


CMD ["supervisord", "-c", "/etc/supervisord.conf"]

#ENTRYPOINT ["/bin/sh"]

#CMD ["/openvertix/scripts/ovx.sh"]

