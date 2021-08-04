#!/usr/bin/python3
from __future__ import print_function
from sys import argv
import lxml.etree as ET
import os
import sys
import time

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

xmlFile = argv[1] #xml file location
domainId = argv[2] #vm name
vmDataStoreLocation = argv[3] #data store location to fetch openpenbula context (flags)

isMonitor = False #check if monitor flag exist, no need to put the vmi stuff
deployDocker = False #docker mode
deployVSock = False #vsock mode
deployNetwork = False #network mode
deployVSockTarget = False #is vsock target VM
vSockMonitorVM = "" #vsock monitor VM

with open(str(vmDataStoreLocation)+"/disk.1", "rb") as f:
	for line in f:
		try:
			x = line.decode("utf-8")
			if "DEPLOY_MONITOR_DOCKER" in x:
				eprint("DEPLOY_MONITOR_DOCKER detected")
				deployDocker = True
			if "DEPLOY_MONITOR_VSOCK" in x:
				deployVSock = True
				eprint("DEPLOY_MONITOR_VSOCK detected")
			if "MONITORING_IP" in x:
				deployNetwork = True
				eprint("MONITORING_IP detected")
			if "KVMI_MONITOR" in x:
				isMonitor = True
				eprint("KVMI_MONITOR detected")
			if "VMI_VSOCK_MONITORING" in x:
				deployVSockTarget = True
				vSockMonitorVM = x.replace("VMI_VSOCK_MONITORING=", "").replace("'","").replace("\n","")
				eprint("VMI_VSOCK_MONITORING detected")
		except Exception as e:
			pass

qemu_namespace = "{{http://libvirt.org/schemas/domain/qemu/1.0}}{0}"

et = ET.parse(xmlFile, ET.XMLParser(strip_cdata=False,remove_blank_text=True))
domain = et.getroot()[0].getparent()

# add the vmi flag for non-monitor
if not isMonitor:
	qemuCMDLine = ET.Element(qemu_namespace.format("commandline"));

	qemuARG1 = ET.Element(qemu_namespace.format("arg"))
	qemuARG1.set("value", "-chardev")
	qemuARG2 = ET.Element(qemu_namespace.format("arg"))
	os.system("mkdir /tmp/"+str(domainId))
	if deployVSockTarget:
		portNo = str(domainId).split("-")[1]
		qemuARG2.set("value", "socket,cid="+str(vSockMonitorVM)+",port="+str(portNo)+",id=chardev0,reconnect=10")
	else:
		qemuARG2.set("value", "socket,path=/tmp/"+str(domainId)+"/vmi-sock,id=chardev0,reconnect=10")
	qemuARG3 = ET.Element(qemu_namespace.format("arg"))
	qemuARG3.set("value", "-object")
	qemuARG4 = ET.Element(qemu_namespace.format("arg"))
	qemuARG4.set("value", "introspection,id=kvmi,chardev=chardev0")
	qemuCMDLine.append(qemuARG1)
	qemuCMDLine.append(qemuARG2)
	qemuCMDLine.append(qemuARG3)
	qemuCMDLine.append(qemuARG4)
	domain.append(qemuCMDLine)

# to enable serial console
devices = domain.find("devices")

serial1 = ET.Element("serial")
serial1.set("type", "pty")
serial1Target = ET.Element("target")
serial1Target.set("port", "0")
serial1.append(serial1Target)

console1 = ET.Element("console")
console1.set("type", "pty")
console1Target = ET.Element("target")
console1Target.set("type", "serial")
console1Target.set("port", "0")
console1.append(console1Target)

devices.append(serial1)
devices.append(console1)


# handle the openvswitch
interfaces = devices.findall("interface")
count = 0
for i in interfaces:
	if count == 0:
		virtualport = ET.Element("virtualport")
		virtualport.set("type", "openvswitch")
		i.append(virtualport)

		# for non sis staff
		source = i.find("source")
		bridge = source.get("bridge")
		tag = bridge.split(".")
		if(len(tag) > 1):
			source.set("bridge", "ovsbr")
			source.set("script", "vif-openvswitch-filtered")
			vlan = ET.Element("vlan")
			tagId = ET.Element("tag")
			tagId.set("id", tag[1].split(",")[0])
			vlan.append(tagId)
			i.append(vlan)

	else:
		if deployDocker: # docker use the second IP address, remove the second interface of the VM
			devices.remove(i)
	count += 1

# vsock monitoring related
if deployVSock:

	portNo = str(domainId).split("-")[1]

	vsock = ET.Element("vsock")
	vsock.set("model", "virtio")
	
	cid = ET.Element("cid")
	cid.set("auto", "no")
	cid.set("address", str(portNo))
	vsock.append(cid)

	alias = ET.Element("alias")
	alias.set("name", "vsock-"+str(portNo))
	vsock.append(alias)

	address = ET.Element("address")
	address.set("type", "pci")
	address.set("domain", "0x0000")
	address.set("bus", "0x00")
	address.set("slot", "0x0b")
	address.set("function", "0x0")
	vsock.append(address)

	devices.append(vsock)

# write all changes to the xml file
et.write(xmlFile,pretty_print=True)


# append config to libvmi config file
libVMIConfigExist = False

with open("/etc/libvmi.conf") as f:
	if str(domainId) in f.read():
		libVMIConfigExist = True

if not libVMIConfigExist:
	config = str(domainId) + " {\n" + "\tostype = \"Linux\";\n" + "\tsysmap = \"/root/System.map.debian2\";\n" + "\tlinux_name = 0x670;\n" + "\tlinux_tasks = 0x3c8;\n" + "\tlinux_mm = 0x418;\n" + "\tlinux_pid = 0x4c8;\n" + "\tlinux_pgd = 0x50;\n" +"}\n"
	with open("/etc/libvmi.conf", "a") as f:
		f.write(config)