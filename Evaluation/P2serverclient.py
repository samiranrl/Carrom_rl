#!/usr/bin/env python
# encoding: utf-8
import subprocess, os, time, shutil, math, random
import numpy as np
from signal import SIGKILL




Ports=[]

for i in range(30000):

    Ports.append(10000+i)


def server_client():
    for i in range(0,50) :
        p1 = None
        p2 = None
        try:
            port1=str(random.choice(Ports))
            port2=str(random.choice(Ports))
            print p1,p2
            cmd = "python ServerP2.py -rs " +str(i)+" -s 1 -p1 "+ port1 +" -p2 "+ port2
            print cmd
            cmd = os.path.join(cmd)
            p1 = subprocess.Popen(cmd.split(' '), shell=False)
            print 'Instance Launched'
            time.sleep(1)
            agentCmd = "python Agent_random.py -p " + port1
            print agentCmd
            agentCmd = os.path.join(agentCmd)
            p2 = subprocess.Popen(agentCmd.split(' '), shell=False)
            print 'Agent1 Launched'
            time.sleep(1)
            agent2Cmd = "python Agent_improved.py -p " + port2
            print agent2Cmd
            agent2Cmd = os.path.join(agent2Cmd)
            p3 = subprocess.Popen(agent2Cmd.split(' '), shell=False)
            print 'Agent2 Launched'

            p1.communicate()
        except Exception as e:
            print e
            return None
        finally:
            try:
                p1.terminate()
                p1.kill()
            except:
                pass
            try:
                p2.terminate()
                p2.kill()
                time.sleep(1)
            except:
                pass
            
            try:
                p3.terminate()
                p3.kill()
                time.sleep(1)
            except:
                pass

if __name__ == '__main__':
    server_client()
