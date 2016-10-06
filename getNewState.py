from Utils import *
import time,datetime
import socket
import sys
from thread import *
import os
import pickle


'''
Play S,A->S'
Input: 
State: {"Black_Locations":[],"White_Locations":[],"Red_Location":[],"Score":0}
Action: [Angle,X,Force] Legal Actions: ? If action is illegal, take random action
Player: 1 or 2
'''
def is_Ended(space, Striker, Coins):
    for coin in space._get_shapes():
        if coin.body.velocity[0]>Static_Velocity_Threshold or coin.body.velocity[1]>Static_Velocity_Threshold:
            return False
    return True

def Play(State,Player,action):
    pygame.init()
    clock = pygame.time.Clock()


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
        if is_Ended(space,Striker,Coins) and Ticks>10:

            #print "Done"
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

            #print "Turn Ended with Score: ", Score, " in ", Ticks, " Ticks"
            return State_new

def tuplise(s) :
    return (float(s[0]),170+(float(s[1])*(460)),float(s[2])*10000)

state,reward = parse_state_message(sys.argv[1]+";REWARD0")
action = tuplise(sys.argv[2].split(","))
print (str(Play(state,1,action)).replace("Vec2d",""))
