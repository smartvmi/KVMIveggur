import os
from sys import argv

domainId = argv[1]
domainSplit = domainId.split("-")
vmDataStoreLocation = argv[2]

deployDocker = False

ipAddress = ""
dns = ""
gateway = ""
sshKey = ""

with open(str(vmDataStoreLocation)+"/disk.1", "rb") as f:
	for line in f:
		try:
			x = line.decode("utf-8")
			if "DEPLOY_MONITOR_DOCKER=" in x:
				deployDocker = True
			if "ETH1_IP=" in x:
				ipAddress = x.replace("ETH1_IP=", "").replace("'","").replace("\n","")
			if "ETH1_DNS=" in x:
				dns = x.replace("ETH1_DNS=", "").replace("'","").replace("\n","")
			if "ETH1_GATEWAY=" in x:
				gateway = x.replace("ETH1_GATEWAY=", "").replace("'","").replace("\n","")
			if "SSH_PUBLIC_KEY=" in x:
				sshKey = x.replace("SSH_PUBLIC_KEY=", "").replace("'","").replace("\n","")
		except Exception as e:
			pass

if deployDocker:

	os.system("mkdir -p /var/lib/one/datastores/102/"+domainSplit[1]+"/vmi-docker/")
	os.system("cp /var/lib/one/docker-template/* /var/lib/one/datastores/102/"+domainSplit[1]+"/vmi-docker/")

	with open("/var/lib/one/datastores/102/"+domainSplit[1]+"/vmi-docker/libvmi.conf", "a+") as f:
		if str(domainId) not in f.read():
			config = str(domainId) + " {\n" + "\tostype = \"Linux\";\n" + "\tsysmap = \"/home/vmi/System.map.debian2\";\n" + "\tlinux_name = 0x670;\n" + "\tlinux_tasks = 0x3c8;\n" + "\tlinux_mm = 0x418;\n" + "\tlinux_pid = 0x4c8;\n" + "\tlinux_pgd = 0x50;\n" +"}\n"
			f.write(config)

	with open("/var/lib/one/datastores/102/"+domainSplit[1]+"/vmi-docker/sshkey", "a+") as f:
		f.write(sshKey)

	os.chdir("/var/lib/one/datastores/102/"+domainSplit[1]+"/vmi-docker/")
	os.system("docker build -t "+domainId+" .")
	#os.system("docker run -p "+ipAddress+":"+domainSplit[1]+":22 --name "+domainId+" -t -dit -v /tmp/"+domainId+"/:/tmp/"+domainId+"/ "+domainId)
	#os.system("docker run -p "+domainSplit[1]+":22 --name "+domainId+" -t -dit -v /tmp/"+domainId+"/:/tmp/"+domainId+"/ "+domainId)
	netName = "sis-staff"
	if ".12." in ipAddress:
		netName = "sis-stud"
	elif ".13." in ipAddress:
		netName = "sis-csec"
	
	os.system("docker run --net="+netName+" --ip="+ipAddress+" --name "+domainId+" -t -dit -v /tmp/"+domainId+"/:/tmp/"+domainId+"/ "+domainId)

	# with open("/tmp/test.txt", "a") as f:
	# 	f.write("AAAAA\n")
	# 	f.write(ipAddress)
	# 	f.write(dns)
	# 	f.write(gateway)
	# 	f.write("docker run -p "+ipAddress+":"+domainSplit[1]+":22 --name "+domainId+" -t -dit -v /tmp/"+domainId+"/:/tmp/"+domainId+"/ "+domainId)
	# 	f.write("\n")