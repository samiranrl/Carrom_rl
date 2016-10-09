import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', dest="filename", type=str,
                        default="filename",
                        help='Name of the file you want stats on')


args=parser.parse_args()


f=open(args.filename,"r")
raw=f.read()
f.close()
raw=raw.split("\n")
raw.pop()
raw=[i.split(" ") for i in raw]
raw=zip(*raw)


Turns_mean=round(np.mean([int(i) for i in raw[0]]),2)
Turns_std=round(np.std([int(i) for i in raw[0]]),2)

Clear=round(np.mean([float(i) for i in raw[1]]),2)
print "To clear the board: "
print "Average Turns: ", Turns_mean
print "Std Turns: ", Turns_std
print "Average Time: ", Clear," s"
print "No of Carrom Plays: ", len(raw[0])
