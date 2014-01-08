#!/usr/bin/python

import paramiko
import time
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-r", "--router", dest="router", default="192.168.0.1",
				  help="ip of router", metavar="ROUTER")
parser.add_option("-u", "--username", dest="username", default="app",
				  help="username", metavar="USERNAME")
parser.add_option("-p", "--password", dest="password", default="com8&#wDs2*1er",
				  help="password", metavar="PASSWORD")
parser.add_option("-l", "--log", dest="log", default=False,
				  help="logging of responses", metavar="LOG")
parser.add_option("-s", "--ssh", dest="ssh", default=False,
				  help="open ssh port", metavar="SSH")
			
(options, args) = parser.parse_args()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
while True:
	try:
		ssh.connect(options.router,
			username=options.username,
			password=options.password,
			timeout=5
		)
		break
	except Exception as e:
		print("> Could not connect. Trying again in three seconds")
	time.sleep(3)
	
def send_wait(chan, msg, t):
	chan.send(msg + "\r\n")
	time.sleep(t)
	if options.log:
		x = chan.recv(1024)
		sys.stdout.write(x)
		sys.stdout.flush()

print("> Connected")
chan = ssh.invoke_shell()
if options.ssh:
	print("> Waiting for end of boot...")
	time.sleep(60 * 3)
	print("> Opening ssh port...")
	send_wait(chan, "iptables -I LOCAL_MANAGEMENT_CONTROL 1 -p tcp --dport 22 -j ACCEPT", 1)

print("> Activating wifi...")
send_wait(chan, "cli", 3)
send_wait(chan, "rg", 1)
send_wait(chan, "Wls 1", 1)

chan.close()
ssh.close()
print("> Done")
