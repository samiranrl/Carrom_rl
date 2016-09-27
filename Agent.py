from Utils import *
import time
import socket
import sys
from thread import *

host = '127.0.0.1'
port = 12121

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))


while 1:
        tm = s.recv(1024)	
        a=str(random.random()*6.28)+ ',' + str(random.randrange(170,630))+','+str(random.randrange(1000,10000))
	
	try:
		s.send(a)
	except:
		print "Error in sending:",  a
s.close()
