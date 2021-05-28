import os
from sys import argv

domainId = argv[1]
domainSplit = domainId.split("-")

os.system("mkdir -p /var/lib/one/datastores/102/"+domainSplit[1]+"/vmi-docker/")
os.system("cp /var/lib/one/docker-template/* /var/lib/one/datastores/102/"+domainSplit[1]+"/vmi-docker/")

with open("/var/lib/one/datastores/102/"+domainSplit[1]+"/vmi-docker/libvmi.conf", "a+") as f:
	if str(domainId) not in f.read():
		config = str(domainId) + " {\n" + "\tostype = \"Linux\";\n" + "\tsysmap = \"/home/vmi/System.map.debian2\";\n" + "\tlinux_name = 0x670;\n" + "\tlinux_tasks = 0x3c8;\n" + "\tlinux_mm = 0x418;\n" + "\tlinux_pid = 0x4c8;\n" + "\tlinux_pgd = 0x50;\n" +"}\n"
		f.write(config)

os.chdir("/var/lib/one/datastores/102/"+domainSplit[1]+"/vmi-docker/")
os.system("docker build -t "+domainId+" .")
os.system("docker run -p "+domainSplit[1]+":22 --name "+domainId+" -t -dit -v /tmp/"+domainId+"/:/tmp/"+domainId+"/ "+domainId)