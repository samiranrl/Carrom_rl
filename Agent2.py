from Utils import *
import time
import socket
import sys
from thread import *

host = '127.0.0.1'
port = 34343

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))


while 1:
        tm = s.recv(1024)	
        a=str(random.random()*6.28)+ ',' + str(random.random())+','+str(random.random())
	
	try:
		s.send(a)
	except:
		print "Error in sending:",  a
s.close()
