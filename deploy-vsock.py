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

# check whether the VM is up by probing SSH port (22) -> vsock somehow fail if the VM is not yet booted
def ssh_port_check(ip):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex((ip,22))
	eprint("TARGET : " + str(ip))
	eprint("PORT RESULT : " + str(result))
	sock.close()
	return result

domainId = argv[1]
vmDataStoreLocation = argv[2]

deployVSock = False
targetVMVsock = ""
ipAddress = ""

# with open(str(vmDataStoreLocation)+"/disk.1", "rb") as f:
# 	for line in f:
# 		try:
# 			x = line.decode("utf-8")
# 			if "DEPLOY_MONITOR_VSOCK" in x:
# 				deployVSock = True
# 		except Exception as e:
# 			pass

# if deployVSock:
# 	with open(str(vmDataStoreLocation)+"/disk.1", "rb") as f:
# 		for line in f:
# 			try:
# 				x = line.decode("utf-8")
# 				#fetch the machine target
# 				if "VMI_TARGET=" in x:
# 					targetVMVsock = x.replace("VMI_TARGET=", "").replace("'","").replace("\n","")
# 					eprint("VMI_TARGET detected : " + str(targetVMVsock))
# 				if "ETH0_IP=" in x:
# 					ipAddress = x.replace("ETH0_IP=", "").replace("'","").replace("\n","")
# 			except Exception as e:
# 				pass


# 	portNo = str(domainId).split("-")[1]

# 	while ssh_port_check(str(ipAddress)) != 0:
# 		time.sleep(5)

# 	time.sleep(5)

# 	cmd = "socat UNIX-LISTEN:/tmp/one-"+str(targetVMVsock)+"/vmi-sock,unlink-early,fork VSOCK-CONNECT:"+str(portNo)+":1,fork &"
# 	eprint("EXECUTING : " + str(cmd))
# 	os.system(cmd)

# 	time.sleep(1)

# 	cmd2 = "chmod 777 /tmp/one-"+str(targetVMVsock)+"/vmi-sock"
# 	eprint("EXECUTING : " + str(cmd2))
# 	os.system(cmd2)