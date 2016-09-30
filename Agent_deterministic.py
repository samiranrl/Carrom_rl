from Utils import *
import time
import socket
import math
import sys
from thread import *
import ast
host = '127.0.0.1'
port = 12121

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

#170:630
while 1:
        tm = s.recv(1024)
        try:
            S,r=parse_state_message(tm)
            #print S,r
        except:
            print "Something went wrong",tm
        try:
            a=str(3.14/2)+ ',' + str(0.1)+','+str(0.75)
            s.send(a)
        except:
            print "Error in sending:",  a
s.close()
