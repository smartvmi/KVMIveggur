import os
from sys import argv
import sys
import subprocess

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

deployId = sys.argv[1]

eprint("DESTROYING : " + str(deployId))

if "one-" in deployId:
	domainId = deployId
else:
	domainId = subprocess.check_output("virsh --connect qemu:///system domname " + deployId, shell=True).decode(sys.stdout.encoding).strip()
	domainId.replace(" ","")
	domainId.replace("\n", "")

domainSplit = domainId.split("-")

os.system("rm -Rf /tmp/"+domainId)
os.system("docker rm "+domainId+" --force")
os.system("docker image rm "+domainId+":latest --force")
os.system("rm -Rf /var/lib/one/datastores/102/"+domainSplit[1]+"/vmi-docker/")

# destroy vsock
os.system("sudo kill -9 $(ps ax | grep socat | grep "+str(domainSplit[1])+" | awk '{print $1}')")