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
it=0
#170:630

A=[str(3.14/2)+ ',' + str(0.5)+','+str(1),str(3.14/5)+ ',' + str(0.5)+','+str(1),str(3.14*(3/2))+ ',' + str(0.5)+','+str(1)]

while 1:

    tm = s.recv(1024)
    try:
        S,r=parse_state_message(tm)
        #print S,r
    except:
        print "Something went wrong",tm

        
    if  S["White_Locations"]!=None or S["Black_Locations"]!=None or S["Red_Location"]!=None:
        
        to_hit=random.choice(S["White_Locations"]+S["Black_Locations"]+S["Red_Location"])
        loc = (400,145)
        angle=math.atan2((to_hit[1]-loc[1]),(to_hit[0]-loc[0]))
        if angle < 0:
            angle = angle + 2*3.14

        a=str(angle)+ ',' + str(0.5)+','+str(0.5+(random.random()/2))
    else:
        a=None
    try:
        if random.random()<0.2:
            a=str(random.random()*6.28)+ ',' + str(random.random())+','+str(random.random())

        a=A[it%3]
        s.send(a)
        it+=1
        print "sent: ", a
    except:
        print "Error in sending:",  a
s.close()
