from Utils import *
import time,datetime
import socket
import sys
from thread import *
import os
import pickle
import argparse
from random import gauss

global Vis
global Total_Ticks

Total_Ticks=0



parser = argparse.ArgumentParser()
parser.add_argument('-v', '--visualization', dest="Vis", type=int,
                        default=0,
                        help='Visualization on/off')

parser.add_argument('-rr', '--', dest="RENDER_RATE", type=int,
                        default=10,
                        help='Render every nth frame')

parser.add_argument('-p', '--port', dest="PORT1", type=int,
                        default=12121,
                        help='Port for incoming connection')

parser.add_argument('-rs', '--random-seed', dest="RNG_SEED", type=int,
                        default=0,
                        help='Random Seed')

parser.add_argument('-s', '--stochasticity', dest="stochasticity", type=int,
                        default=1,
                        help='Turn Stochasticity on/off')


args=parser.parse_args()

RENDER_RATE=args.RENDER_RATE
Vis=args.Vis
PORT1=args.PORT1

random.seed(args.RNG_SEED)
HOST = '127.0.0.1'   # Symbolic name meaning all available interfaces

t=time.time()

global Stochasticity
Stochasticity=args.stochasticity
if Stochasticity==1:
    noise=0.0005
else:
    noise=0


# Handle exceptions here

# Exception handlers here

timeout_msg = "TIMED OUT"
timeout_period = 0.5
def is_Ended(space):
    for shape in space._get_shapes():
        if abs(shape.body.velocity[0])>Static_Velocity_Threshold or abs(shape.body.velocity[1])>Static_Velocity_Threshold:
            return False
    return True

def requestAction(conn1) :
    try : 
        data=conn1.recv(1024)
    except :
        data = timeout_msg
    finally :
        return data
    
def sendState(state,conn1):
    try:
        conn1.send(state)
    except socket.error:
        print "Aborting, player timeout"
        sys.exit()

    return True
    
'''
Play S,A->S'
Input: 
State: {"Black_Locations":[],"White_Locations":[],"Red_Location":[],"Score":0}
Action: [Angle,X,Force] Legal Actions: ? If action is illegal, take random action
Player: 1 or 2
Vis: Visualization? Will be handled later
'''

def Play(State,Player,action):
    #print "Turn Started with Score: ", State["Score"]
    #print "Coins: ", len(next_State["Black_Locations"]),len(next_State["White_Locations"]),len(next_State["Red_Location"])
    

    global Vis
    pygame.init()
    clock = pygame.time.Clock()

    if Vis==1:
        screen = pygame.display.set_mode((Board_Size, Board_Size))
        pygame.display.set_caption("Carrom RL Simulation")

    space = pymunk.Space(threaded=True)
    Score = State["Score"]
    prevScore = State["Score"]


    # pass through object // Dummy Object for handling collisions
    passthrough = pymunk.Segment(space.static_body, (0, 0), (0, 0), 5)
    passthrough.collision_type = 2
    passthrough.filter = pymunk.ShapeFilter(categories=0b1000)

    init_space(space)
    init_walls(space)
    Holes=init_holes(space)
    ##added
    BackGround = Background('use_layout.png', [-30,-30])

    Coins=init_coins(space,State["Black_Locations"],State["White_Locations"],State["Red_Location"],passthrough)
    #load_image("layout.jpg")
    Striker=init_striker(space,Board_Size/2+10, passthrough,action, Player)
        
    if Vis==1:
        draw_options = pymunk.pygame_util.DrawOptions(screen)


    Ticks=0
    Foul=False
    Pocketed=[]


    #print "Force: ",1000-+action[2]*1000
    Queen_Pocketed=False
    Queen_Flag=False
    while 1: 

        if Ticks%RENDER_RATE==0 and Vis==1:
            Local_VIS=True
        else:
            Local_VIS=False

        Ticks+=1
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit(0)

        if Local_VIS==1:
            screen.blit(BackGround.image, BackGround.rect)
            space.debug_draw(draw_options)

        space.step(1/TIME_STEP)
        #print Striker[0].position
        for hole in Holes:
            if dist(hole.body.position,Striker[0].position)<Hole_Radius-Striker_Radius+(Striker_Radius*0.75):
                Foul=True
                for coin in space._get_shapes():
                    if coin.color==Striker_Color:
                        space.remove(coin,coin.body)
                        break


        for hole in Holes:
            for coin in space._get_shapes():
                if dist(hole.body.position,coin.body.position)<Hole_Radius-Coin_Radius+(Coin_Radius*0.75):
                    if coin.color == Black_Coin_Color:
                        Score+=1
                        Pocketed.append((coin,coin.body))
                        space.remove(coin,coin.body)
                    if coin.color == White_Coin_Color:
                        Score+=1
                        Pocketed.append((coin,coin.body))
                        space.remove(coin,coin.body)
                    if coin.color == Red_Coin_Color:
                        #Score+=3
                        Pocketed.append((coin,coin.body))
                        space.remove(coin,coin.body)
                        Queen_Pocketed=True


        if Local_VIS==1:
            font = pygame.font.Font(None, 25)
            text = font.render("Player 1 Score: "+str(Score), 1, (220, 220, 220))
            screen.blit(text, (Board_Size/3 + 67,780,0,0))

            text = font.render("Time Elapsed: "+str(round(time.time()-t,2)), 1, (50, 50, 50))
            screen.blit(text, (Board_Size/3 + 57,25,0,0))
            if Ticks==1:
                length=Striker_Radius+action[2]/500.0 # The length of the line denotes the action
                startpos_x=action[1]
                angle=action[0]
                if Player==2:
                    startpos_y=145
                else:
                    startpos_y=Board_Size - 136
                endpos_x=(startpos_x+cos(angle)*length)
                endpos_y=(startpos_y-(length)*sin(angle))
                pygame.draw.line(screen, (50,255,50), (endpos_x, endpos_y), (startpos_x,startpos_y),3)
                pygame.draw.circle(screen,(50,255,50), (int(endpos_x), int(endpos_y)), 5)
            pygame.display.flip()
            if Ticks==1:
                time.sleep(1)
            clock.tick()
        
        # Do post processing and return the next State
        if is_Ended(space) or Ticks>TICKS_LIMIT:
            State_new={"Black_Locations":[],"White_Locations":[],"Red_Location":[],"Score":0}

            for coin in space._get_shapes():
                    if coin.color == Black_Coin_Color:
                        State_new["Black_Locations"].append(coin.body.position)
                    if coin.color == White_Coin_Color:
                        State_new["White_Locations"].append(coin.body.position)
                    if coin.color == Red_Coin_Color:
                        State_new["Red_Location"].append(coin.body.position)
            if Foul==True:
                print "Foul!"
                for coin in Pocketed:
                    if coin[0].color == Black_Coin_Color:
                        State_new["Black_Locations"].append(ret_pos(State_new))
                        Score-=1
                    if coin[0].color == White_Coin_Color:
                        State_new["White_Locations"].append(ret_pos(State_new))
                        Score-=1
                    if coin[0].color == Red_Coin_Color:
                        State_new["Red_Location"].append(ret_pos(State_new))
                        #Score-=3
            # What will happen if there is a clash?? Fix it later


        

            if (Queen_Pocketed==True and Foul==False):
                if len(State_new["Black_Locations"]) + len(State_new["White_Locations"]) == 18:
                    print "The queen cannot be the first to be pocketed: Player ", Player
                    State_new["Red_Location"].append(ret_pos(State_new))
                else:
                    if Score-prevScore>0:
                        Score+=3
                        print "Queen pocketed and covered in one shot"
                    else:
                        Queen_Flag=True

            global Total_Ticks
            Total_Ticks+=Ticks
            State_new["Score"]=Score
            print "Turn Ended with Score: ", Score, " in ", Ticks, " Ticks"
            print "Coins: ", len(State_new["Black_Locations"]),"B ", len(State_new["White_Locations"]),"W ",len(State_new["Red_Location"]),"R"
            return State_new,Queen_Flag



def don():
    s1.close()
    conn1.close()
    sys.exit()



def tuplise(s) :

    return (round(float(s[1]),4),round(float(s[0]),4),round(float(s[2]),4))

def validate(action) :
    print "Action Recieved: ",action
    angle=action[0]
    position=action[1]
    force=action[2]
    if angle<-45 or angle >225:
        print "Invalid Angle, taking random angle",
        angle=random.randrange(-45,270)
        print "which is ", angle
    if position<0 or position>1:
        print "Invalid position, taking random position"
        position=random.random()    
    if force<0 or force>1:
        print "Invalid force, taking random position"
        force=random.random()  
    global Stochasticity
    if Stochasticity==1:
        angle=angle+randrange(-5,5)
        if angle<-45:
            angle=-45
        if angle>225:
            angle=225

    if angle<0:
        angle=360+angle
    angle=angle/180.0*3.14
    position=170+(float(max(min(float(action[1]) + gauss(0,noise),1),0))*(460))
    force=MIN_FORCE+float(max(min(float(action[2]) + gauss(0,noise),1),0))*MAX_FORCE

    action=(angle,position,force)
    #print "Final action", action
    return action

if __name__ == '__main__':


    s1=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s1.bind((HOST, PORT1))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    s1.listen(1)
    conn1,addr1=s1.accept()
    conn1.settimeout(timeout_period);
    
    winner = 0
    reward1 = 0
    score1 = 0
    reward2 = 0
    score2 = 0
    #State={"Black_Locations":B,"White_Locations":W,"Red_Location":R,"Score":0, Message:" "}
    State={'White_Locations': [(400,368),(437,420), (372,428),(337,367), (402,332), (463,367), (470,437), (405,474), (340,443)], 'Red_Location': [(400, 403)], 'Score': 0, 'Black_Locations': [(433,385),(405,437), (365,390), (370,350), (432,350), (467,402), (437,455), (370,465), (335,406)]}  
    next_State=State
    # Black Coins, White Coins, Red Coin, VISualization : On/Off, Score, Flip the board? 0 - no 1 - yes
    it=1





    while it<500: # Number of Chances given to each player
        it+=1
        prevScore = next_State["Score"]
        sendState(str(next_State) + ";REWARD" + str(reward1),conn1)
        s=requestAction(conn1)
        if not s :#response empty
            print "No response from player 1"
            sys.exit()
        elif s == timeout_msg:
            print "No response from player 1"
            sys.exit()
        else :
            action=tuplise(s.replace(" ","").split(','))
            
        next_State,Queen_Flag=Play(next_State,1,validate(action))
        reward1 = next_State["Score"] - prevScore
        prevScore = next_State["Score"]
        score1 += reward1
        print " turns: "+str(it)
        while Queen_Flag: # Extra turn

            print "Pocketed Queen, pocket any coin in this turn to cover it"
            it+=1
            prevScore = next_State["Score"]
            sendState(str(next_State) + ";REWARD" + str(reward1),conn1)
            s=requestAction(conn1)
            if not s :#response empty
                print "Empty P1";
            elif s == timeout_msg:
                winner = 2
                break
            else :
                action=tuplise(s.replace(" ","").split(','))    
            next_State,Queen_Flag=Play(next_State,1,validate(action))
            reward1 = next_State["Score"] - prevScore
            prevScore = next_State["Score"]
            if reward1>0:
                next_State["Score"]+=3
                print "Successfully covered the queen"
            else:
                print "Could not cover the queen"
                next_State["Red_Location"].append(ret_pos(next_State))
            score1+= reward1
            print " turns: "+str(it)
        if len(next_State["Black_Locations"])==0 and len(next_State["White_Locations"])==0:
            if len(next_State["Red_Location"])>0:
                next_State["Black_Locations"].append(ret_pos(next_State))
                next_State["Score"]-=1
                print "Failed to clear queen, getting another turn"
            else:
                break

    print "Cleared Board in " + str(it)," turns."
    f=open("logS1.txt","a")
    f.write(str(it)+" "+str(round(time.time()-t,0))+"\n")
    f.close()
    don()

