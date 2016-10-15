from thread import *
import time, socket, sys, argparse,random



parser = argparse.ArgumentParser()
parser.add_argument('-np', '--num-players', dest="NUM_PLAYERS", type=int,
                        default=1,
                        help='1 Player or 2 Player')
parser.add_argument('-p', '--port', dest="PORT", type=int,
                        default=12121,
                        help='Port')
parser.add_argument('-rs', '--random-seed', dest="RNG_SEED", type=int,
                        default=0,
                        help='Random Seed')
parser.add_argument('-c', '--color', dest="COLOR", type=str,
                        default="Black",
                        help='Legal color to pocket')
args=parser.parse_args()


host = '127.0.0.1'
port = args.PORT
num_players=args.NUM_PLAYERS
random.seed(args.RNG_SEED)
color = args.COLOR

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port)) # The logic to connect to the server must be implemented by you, according to the progamming language

while 1:
        tm = s.recv(1024)

        # Your agent's logic should be coded here	
        a= str(random.random())+ ',' +str(random.randrange(-45,225))+','+str(random.random())
	
	try:
		s.send(a)
	except:
		print "Error in sending:",  a
		print "Closing Connection"
		break
s.close()
