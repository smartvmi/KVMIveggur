# syntax=docker/dockerfile:1
FROM vmi-master
COPY System.map.debian2 /home/vmi/
COPY libvmi.conf /etc/
COPY sshkey /root/.ssh/authorized_keys
RUN echo 'root:password' | chpasswd