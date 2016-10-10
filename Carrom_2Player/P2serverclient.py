#!/usr/bin/env python
# encoding: utf-8
import subprocess, os, time, shutil, math, random
import numpy as np
from signal import SIGKILL

def server_client():
    for i in range(0,50) :
        pros = []
        p1 = None
        p2 = None
        try:
            cmd = "python ServerP2.py -rs " +str(i)+" -s 1 -p1 12422 -p2 54353"
            print cmd
            cmd = os.path.join(cmd)
            p1 = subprocess.Popen(cmd.split(' '), shell=False)
            print 'Instance Launched'
            time.sleep(1)
            agentCmd = "python Agent_random.py -p 12422"
            print agentCmd
            agentCmd = os.path.join(agentCmd)
            p2 = subprocess.Popen(agentCmd.split(' '), shell=False)
            print 'Agent1 Launched'
            agent2Cmd = "python Agent_improved.py -p 54353"
            print agent2Cmd
            agent2Cmd = os.path.join(agent2Cmd)
            p3 = subprocess.Popen(agent2Cmd.split(' '), shell=False)
            print 'Agent2 Launched'
            pros.append(p1)
            pros.append(p2)
            pros.append(p3)
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
