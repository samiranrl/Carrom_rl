import subprocess,argparse,os,time

parser = argparse.ArgumentParser()

parser.add_argument('-np', '--num-players', dest="NUM_PLAYERS", type=int,
                        default=1,
                        help='1 Player or 2 Player')

parser.add_argument('-ne', '--num-experiments', dest="NUM_EXPERIMENTS", type=int,
                        default=1,
                        help='Number of experiments to run')

parser.add_argument('-v', '--Visualization', dest="VIS", type=int,
                        default=0,
                        help='Visualization')

parser.add_argument('-p1', '--port1', dest="PORT1", type=int,
                        default=12121,
                        help='Port 1')

parser.add_argument('-p2', '--port2', dest="PORT2", type=int,
                        default=34343,
                        help='Port 2')

parser.add_argument('-rr', '--render-rate', dest="RENDER_RATE", type=int,
                        default=10,
                        help='Render every nth frame')

parser.add_argument('-n', '--noise', dest="NOISE", type=int,
                        default=1,
                        help='Turn noise on/off')

parser.add_argument('-rs', '--random-seed', dest="RNG_SEED", type=int,
                        default=0,
                        help='Random Seed')

parser.add_argument('-a1', '--agent-1-location', dest="A1", type=str,
                        default='carrom_agent/start_agent.py',
                        help='relative/full path to agent')

parser.add_argument('-a2', '--agent-2-location', dest="A2", type=str,
                        default='carrom_agent/start_agent.py',
                        help='relative/full path to agent')

args=parser.parse_args()

render_rate=args.RENDER_RATE
num_players=args.NUM_PLAYERS
vis=args.VIS
port1=args.PORT1
port2=args.PORT2
rng=args.RNG_SEED
noise=args.NOISE
a1=args.A1
a2=args.A2
ne=args.NUM_EXPERIMENTS


for i in range(0,args.NUM_EXPERIMENTS) :
    try:
        if ne>1:
            rng=i
        if num_players==1:

            cmd='python 1_player_server/start_server.py'+' -v '+str(vis)+' -rr '+str(render_rate)+' -n '+str(noise)+' -p '+str(port1)+' -rs '+str(rng)
            cmd = os.path.join(cmd)
            print cmd
            p1 = subprocess.Popen(cmd.split(' '), shell=False)
            print 'Launched Server'
            time.sleep(1)
            cmd1='python '+a1+' -p '+str(port1)+' -rs '+str(rng)+' -np 1'
            cmd1 = os.path.join(cmd1)
            print cmd1
            p2 = subprocess.Popen(cmd1.split(' '), shell=False)
            print 'Launched Agent'
            p1.communicate()


        if num_players==2:
            cmd='python 2_player_server/start_server.py'+' -v '+str(vis)+' -rr '+str(render_rate)+' -n '+str(noise)+' -p1 '+str(port1)+' -p2 '+str(port2)+' -rs '+str(rng)
            print cmd
            p1 = subprocess.Popen(cmd.split(' '), shell=False)
            print 'Launched Server'
            time.sleep(1)
            cmd1='python '+a1+' -p '+str(port1)+' -rs '+str(rng)+' -np 2'+' -c White' 
            print cmd1
            p2 = subprocess.Popen(cmd1.split(' '), shell=False)
            print 'Launched Player 1 Agent'
            time.sleep(1)
            cmd2='python '+a2+' -p '+str(port2)+' -rs '+str(rng)+' -np 2'+' -c Black' 
            print cmd2
            p3 = subprocess.Popen(cmd2.split(' '), shell=False)
            print 'Launched Player 2 Agent'
            p1.communicate()
    except Exception as e:
        print "Error: ",e
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

