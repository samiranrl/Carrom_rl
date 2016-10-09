from Utils import *
import time
import socket
import math
import sys
from thread import *
import ast
import argparse



parser = argparse.ArgumentParser()


parser.add_argument('-p', '--port', dest="PORT", type=int,
                        default=12121,
                        help='Port')


args=parser.parse_args()




host = '127.0.0.1'
port = args.PORT

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

#170:630
while 1:
        tm = s.recv(1024)
        try:
            S,r=parse_state_message(tm)
            #print S,r
        except:
            print "Something went wrong"

        try: 
            
            if  S["White_Locations"]!=None or S["Black_Locations"]!=None or S["Red_Location"]!=None:
                if port==12121:
                    to_hit=random.choice(S["White_Locations"]+S["Red_Location"])
                else:
                    to_hit=random.choice(S["Red_Location"]+S["Black_Locations"])

                loc = (400,145)
                angle=math.atan2((to_hit[1]-loc[1]),(to_hit[0]-loc[0]))
                if angle < 0:
                    angle = angle + 2*3.14

                a=str(angle)+ ',' + str(0.5)+','+str(0.5+(random.random()/2))
        except:
            a=str(random.random()*6.28)+ ',' + str(random.random())+','+str(random.random())
            print "Taking Random"
        try:
            if random.random()<0:
                a=str(random.random()*6.28)+ ',' + str(random.random())+','+str(random.random())
                print "Taking Random due to epsilon greedy"
            print "Sending",a                
            s.send(a)
        except:
            print "Error in sending:",  a
	    print "Closing Connection"
	    break
s.close()
