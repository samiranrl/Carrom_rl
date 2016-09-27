from Utils import *
import time,datetime
import socket
import sys
from thread import *
import os
import pickle

HOST = '127.0.0.1'   # Symbolic name meaning all available interfaces
PORT1 = 12121 # Arbitrary non-privileged port
PORT2 = 34343  # Arbitrary non-privileged port

t=time.time()


global VIS
VIS=1
timeout_msg = "TIMED OUT"
def is_Ended(space, Striker, Coins):
    for coin in space._get_shapes():
        if coin.body.velocity[0]>Static_Velocity_Threshold or coin.body.velocity[1]>Static_Velocity_Threshold:
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
    conn1.send(state)
    return True
    
'''
Play S,A->S'
Input: 
State: {"Black_Locations":[],"White_Locations":[],"Red_Location":[],"Score":0}
Action: [Angle,X,Force] Legal Actions: ? If action is illegal, take random action
Player: 1 or 2
VIS: VISualization? Will be handled later
'''

def Play(State,Player,action):
    global VIS
    pygame.init()
    clock = pygame.time.Clock()

    if VIS==1:
        screen = pygame.display.set_mode((Board_Size, Board_Size))
        pygame.display.set_caption("Beta Carrom")

    space = pymunk.Space(threaded=True)
    Score = State["Score"]


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
        
    if VIS==1:
        draw_options = pymunk.pygame_util.DrawOptions(screen)


    Ticks=0
    while Ticks<1000: # fuse in case something goes wrong
        Foul=False
        Foul_List=[]
        Ticks+=1
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit(0)

        if VIS==1:

            #screen.fill(Board_Color)
            screen.fill([255, 255, 255])
            screen.blit(BackGround.image, BackGround.rect)
            space.debug_draw(draw_options)

        
        for hole in Holes:
            for coin in space._get_shapes():
                if dist(hole.body.position,coin.body.position)<Hole_Radius-Coin_Radius+(Coin_Radius*0.75):
                    if coin.color == Striker_Color and dist(hole.body.position,coin.body.position)<Hole_Radius-Striker_Radius+(Striker_Radius*0.75):
                        Foul=True
                        space.remove(coin,coin.body)
                    if Foul==True and coin.color in [White_Coin_Color,Red_Coin_Color,Black_Coin_Color]:
                        Foul_List.append(coin)
                        pass
                    if coin.color == Black_Coin_Color:
                        Score+=10
                        space.remove(coin,coin.body)

                    if coin.color == White_Coin_Color:
                        Score+=20
                        space.remove(coin,coin.body)
                    if coin.color == Red_Coin_Color:
                        Score+=50
                        space.remove(coin,coin.body)


        space.step(1/8.0)

        #print space.shapes[1]

        if VIS==1:
            font = pygame.font.Font(None, 25)
            text = font.render("SCORE: "+str(Score)+"  FPS: "+str(int(clock.get_fps()))+" REALTIME :"+ str(round(time.time()-t,2)) + "s", 1, (10, 10, 10))
            screen.blit(text, (20,Board_Size/10,0,0))
            pygame.display.flip()
            clock.tick()




        # Do post processing and return the next State

        if is_Ended(space,Striker,Coins) and Ticks>10:

            print "Done"
            State_new={"Black_Locations":[],"White_Locations":[],"Red_Location":[],"Score":0}
            State_new["Score"]=Score
            for coin in space._get_shapes():
                    if coin.color == Black_Coin_Color:
                        State_new["Black_Locations"].append(coin.body.position)
                    if coin.color == White_Coin_Color:
                        State_new["White_Locations"].append(coin.body.position)
                    if coin.color == Red_Coin_Color:
                        State_new["Red_Location"].append(coin.body.position)

            for coin in Foul_List:
                    if coin.color == Black_Coin_Color:
                        State_new["Black_Locations"].append(coin.body.position)
                    if coin.color == White_Coin_Color:
                        State_new["White_Locations"].append(coin.body.position)
                    if coin.color == Red_Coin_Color:
                        State_new["Red_Location"].append(coin.body.position)

            print "Turn Ended with Score: ", Score, " in ", Ticks, " Ticks"
            return State_new






def tuplise(s) :
    return (float(s[0]),float(s[1]),float(s[2]))
 
#SAMIRAN:IMPLEMENT last response of the agents are emplty.. account for that also
def validate(action) :
    return True

if __name__ == '__main__':
    B=generate_coin_locations(9)

    W=generate_coin_locations(9)

    R=generate_coin_locations(1)
    numagent=2
    s1=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    timeout_period = 0.5
    try:
        s1.bind((HOST, PORT1))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    s1.listen(1)
    conn1,addr1=s1.accept()
    conn1.settimeout(timeout_period);
    
    if numagent == 2:
        s2=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s2.bind((HOST, PORT2))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
        s2.listen(1)
        conn2,addr2=s2.accept()
        conn2.settimeout(timeout_period);

    
    winner = 0
    reward1 = 0
    score1 = 0
    reward2 = 0
    score2 = 0
    State={"Black_Locations":B,"White_Locations":W,"Red_Location":R,"Score":0}
    next_State=State
    # Black Coins, White Coins, Red Coin, VISualization : On/Off, Score, Flip the board? 0 - no 1 - yes
    it=1
    try:
        while it<1005: # Number of Chances given to each player
            #action=(random.random()*6.28,(random.randrange(Board_Size/10,Board_Size-Board_Size/10),100), random.randrange(100,5000))
            prevScore = next_State["Score"]
            sendState(str(next_State) + "REWARD" + str(reward1),conn1)
            s=requestAction(conn1)
            if not s :#response empty
                print "Empty P1";
            elif s == timeout_msg:
                winner = 2
                break
            else :
                action=tuplise(s.replace(" ","").split(','))
            if(validate(action)) :
                next_State=Play(next_State,1,action)
            else:
                print 'Agent 1 : Invalid action'
            reward1 = next_State["Score"] - prevScore
            prevScore = next_State["Score"]
            score1 = score1 + reward1
            print len(next_State["Black_Locations"]),len(next_State["White_Locations"]),len(next_State["Red_Location"])
            if numagent ==2:
                sendState(str(next_State)+"REWARD" + str(reward2),conn2)
                s=requestAction(conn2)
                if not s: #response empty
                    print "Empty P1";
                elif s == timeout_msg:
                    winner = 1
                    break
                else :
                    action=tuplise(s.replace(" ","").split(','))
                if(validate(action)) :
                    next_State=Play(next_State,2,action)
                else:
                    print 'Agent 1 : Invalid action'
                reward2 = next_State["Score"] - prevScore
                score2 = score2 + reward2
                print len(next_State["Black_Locations"]),len(next_State["White_Locations"]),len(next_State["Red_Location"])
                print "step"+str(it)
            it+=1
            print "Iteration: "+str(it)
            
        if winner == 0 :
            if score1>score2:
                winner= 1
            else:
                winner = 2
        print "Winner is Player " + str(winner)
    finally:
        s1.close()
        conn1.close()
    if numagent == 2:
        s2.close()
        conn2.close()
        print "Done"

