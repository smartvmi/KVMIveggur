import os
from sys import argv
import sys
import subprocess

deployId = argv[1]
domainId = subprocess.check_output("virsh --connect qemu:///system domname " + deployId, shell=True).decode(sys.stdout.encoding).strip()
domainId.replace(" ","")
domainId.replace("\n", "")
domainSplit = domainId.split("-")

os.system("rm -Rf /tmp/"+domainId)
os.system("docker rm "+domainId)
os.system("docker image rm "+domainId+" --force")
os.system("rm -Rf /var/lib/one/datastores/102/"+domainSplit[1]+"/vmi-docker/")

with open("/tmp/test.txt", "a+") as f:
	f.write(''.join(sys.argv[1:]))