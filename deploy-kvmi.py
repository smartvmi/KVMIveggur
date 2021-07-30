#!/usr/bin/python3
from __future__ import print_function
from sys import argv
import lxml.etree as ET
import os
import sys
import time

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

xmlFile = argv[1]
domainId = argv[2]
vmDataStoreLocation = argv[3]

deployDocker = False
deployVSock = False
deployNetwork = False
targetVMVsock = ""

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
		except Exception as e:
			pass

#with open("/tmp/test.txt", "a") as f:
#	f.write("AAAAA")
#	f.write(str(domainId))

qemu_namespace = "{{http://libvirt.org/schemas/domain/qemu/1.0}}{0}"

et = ET.parse(xmlFile, ET.XMLParser(strip_cdata=False,remove_blank_text=True))
domain = et.getroot()[0].getparent()

qemuCMDLine = ET.Element(qemu_namespace.format("commandline"));

qemuARG1 = ET.Element(qemu_namespace.format("arg"))
qemuARG1.set("value", "-chardev")
qemuARG2 = ET.Element(qemu_namespace.format("arg"))
os.system("mkdir /tmp/"+str(domainId))
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
		#eprint(tag)
		if(len(tag) > 1):
			source.set("bridge", "ovsbr")
			source.set("script", "vif-openvswitch-filtered")
			vlan = ET.Element("vlan")
			tagId = ET.Element("tag")
			tagId.set("id", tag[1].split(",")[0])
			vlan.append(tagId)
			i.append(vlan)

	else:
		if deployDocker:
			devices.remove(i)
	count += 1

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

et.write(xmlFile,pretty_print=True)

exist = False

with open("/etc/libvmi.conf") as f:
	if str(domainId) in f.read():
		exist = True

if not exist:
	config = str(domainId) + " {\n" + "\tostype = \"Linux\";\n" + "\tsysmap = \"/root/System.map.debian2\";\n" + "\tlinux_name = 0x670;\n" + "\tlinux_tasks = 0x3c8;\n" + "\tlinux_mm = 0x418;\n" + "\tlinux_pid = 0x4c8;\n" + "\tlinux_pgd = 0x50;\n" +"}\n"
	with open("/etc/libvmi.conf", "a") as f:
		f.write(config)