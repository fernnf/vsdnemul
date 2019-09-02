FROM fedora:latest
RUN dnf update -y
RUN dnf install -y git net-tools snappy-devel gcc gcc-c++



RUN dnf install -y python3-snappy python3-pip python3-devel

WORKDIR /root

RUN git clone https://github.com/fernnf/vsdnorches.git

WORKDIR vsdnorches/

RUN pip3 install -r requirements.txt

RUN /usr/local/bin/crossbar init

WORKDIR .crossbar

RUN rm config.json

COPY config.json .

RUN dnf clean packages

WORKDIR /root/vsdnorches/

ENV PS1="[vsdn:vsdnorches \u@\h]#"

EXPOSE 8080

CMD ["crossbar", "start"]