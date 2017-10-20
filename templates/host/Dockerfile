FROM fedora:latest

RUN dnf -y update &&  dnf install -y openssh-server iputils

RUN dnf -y install tcpdump iperf3 iperf3-devel bing 

RUN mkdir /var/run/sshd

RUN echo 'root:vsdn' | chpasswd

RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"

RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22 

CMD ["/usr/sbin/sshd", "-D"]
