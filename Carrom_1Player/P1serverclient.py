#!/usr/bin/env python
# encoding: utf-8
import subprocess, os, time, shutil, math, random, cma
import numpy as np
from signal import SIGKILL

def server_client():
    for i in range(0,5) :
        pros = []
        p1 = None
        p2 = None
        try:
            cmd = "python ServerP1.py -p 12349 -rs " +str(i)+" -s 0"
            print cmd
            cmd = os.path.join(cmd)
            p1 = subprocess.Popen(cmd.split(' '), shell=False)
            print 'Instance Launched'
            time.sleep(1)
            agentCmd = "python Agent_random.py -p 12349"
            print agentCmd
            agentCmd = os.path.join(agentCmd)
            p2 = subprocess.Popen(agentCmd.split(' '), shell=False)
            print 'Agent Launched'
            pros.append(p1)
            pros.append(p2)
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
                

if __name__ == '__main__':
    server_client()
