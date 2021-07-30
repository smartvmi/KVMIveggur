#!/usr/bin/python3
from __future__ import print_function
from sys import argv
import lxml.etree as ET
import os
import sys
import time
import socket

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

def ssh_port_check():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex(('192.168.11.239',22))
	eprint("PORT RESULT : " + str(result))
	sock.close()
	return result


domainId = argv[1]
vmDataStoreLocation = argv[2]

deployVSock = False
targetVMVsock = ""

with open(str(vmDataStoreLocation)+"/disk.1", "rb") as f:
	for line in f:
		try:
			x = line.decode("utf-8")
			if "DEPLOY_MONITOR_VSOCK" in x:
				deployVSock = True
		except Exception as e:
			pass

if deployVSock:
	with open(str(vmDataStoreLocation)+"/disk.1", "rb") as f:
		for line in f:
			try:
				x = line.decode("utf-8")
				if "VMI_TARGET=" in x:
					targetVMVsock = x.replace("VMI_TARGET=", "").replace("'","").replace("\n","")
			except Exception as e:
				pass


if deployVSock:

	portNo = str(domainId).split("-")[1]

	while ssh_port_check() != 0:
		time.sleep(1)

	cmd = "socat UNIX-LISTEN:/tmp/one-"+str(targetVMVsock)+"/vmi-sock,unlink-early VSOCK-CONNECT:"+str(portNo)+":1,forever,keepalive,fork,reuseaddr &"
	eprint("EXECUTING : " + str(cmd))
	os.system(cmd)

	time.sleep(1)

	cmd2 = "chmod 777 /tmp/one-"+str(targetVMVsock)+"/vmi-sock"
	eprint("EXECUTING : " + str(cmd2))
	os.system(cmd2)