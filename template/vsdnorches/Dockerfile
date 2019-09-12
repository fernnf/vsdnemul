FROM alpine:latest

RUN apk --update add util-linux net-tools iputils python3 py3-pip openssl ca-certificates git bash

RUN apk --update add --virtual build-dependencies python3-dev build-base wget libffi-dev openssl-dev linux-headers snappy-dev

WORKDIR /root

RUN git clone https://github.com/fernnf/vsdnorches.git

WORKDIR vsdnorches/

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

RUN /usr/bin/crossbar init

RUN rm .crossbar/config.json

COPY config.json .crossbar/

RUN  apk del build-dependencies

ENV PS1="[vsdn:vsdnorches \u@\h]#"

CMD ["crossbar", "start"]
