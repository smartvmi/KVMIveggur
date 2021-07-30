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

def ssh_port_check(ip):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex((ip,22))
	eprint("PORT RESULT : " + str(result))
	sock.close()
	return result

domainId = argv[1]
vmDataStoreLocation = argv[2]

deployNetwork = False
targetNetwork = ""
ipAddress = ""

with open(str(vmDataStoreLocation)+"/disk.1", "rb") as f:
	for line in f:
		try:
			x = line.decode("utf-8")
			if "MONITORING_IP" in x:
				deployNetwork = True
				targetNetwork = x.replace("MONITORING_IP=", "").replace("'","").replace("\n","")
			if "ETH0_IP=" in x:
				ipAddress = x.replace("ETH0_IP=", "").replace("'","").replace("\n","")
		except Exception as e:
			pass


if deployNetwork:
	
	while ssh_port_check(str(ipAddress)) != 0:
		time.sleep(1)

	portNo = str(domainId).split("-")[1]
	cmd = "socat UNIX-LISTEN:/tmp/"+str(domainId)+"/vmi-sock,unlink-early TCP:"+str(targetNetwork)+":"+str(portNo)+",forever,keepalive,fork &"
	eprint("EXECUTING : " + str(cmd))
	os.system(cmd)

	time.sleep(1)

	cmd = "chmod 777 /tmp/"+str(domainId)+"/vmi-sock"
	eprint("EXECUTING : " + str(cmd))
	os.system(cmd)