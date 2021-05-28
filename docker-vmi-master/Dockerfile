# syntax=docker/dockerfile:1
FROM debian:buster
RUN apt update && apt install build-essential git vim htop libtool autoconf cmake \
	flex bison libglib2.0-dev libvirt-dev libjson-c-dev libyajl-dev -y
RUN mkdir /home/vmi && cd /home/vmi && \
	git clone https://github.com/bitdefender/libkvmi.git && \
	cd libkvmi && ./bootstrap && ./configure && make && make install
COPY 0001-Removed-superflous-libvirt-dependency-from-KVM-drive.patch /home/vmi
RUN cd /home/vmi && git clone https://github.com/libvmi/libvmi.git && \
	cd libvmi && git checkout 3f5b0d5b3cef8639df4cd7ff52d42e04baf262fd && \
	git apply ../0001-Removed-superflous-libvirt-dependency-from-KVM-drive.patch && \
	mkdir build && cd build && cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local \
	-DENABLE_KVM=ON -DENABLE_XEN=OFF -DENABLE_BAREFLANK=OFF -DENABLE_FILE=OFF \
	-DENABLE_XENSTORE=OFF -DREKALL_PROFILES=OFF && make -j 8 && make install && ldconfig
WORKDIR /home/vmi