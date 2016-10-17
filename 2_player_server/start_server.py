from Utils import *
import time
import datetime
import socket
import sys
from thread import *
import os
import pickle
import argparse
from random import gauss

global Vis

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--Visualization', dest="Vis", type=int,
                    default=0,
                    help='Visualization')

parser.add_argument('-p1', '--port1', dest="PORT1", type=int,
                    default=12121,
                    help='Port 1')

parser.add_argument('-p2', '--port2', dest="PORT2", type=int,
                    default=34343,
                    help='Port 2')

parser.add_argument('-rr', '--', dest="RENDER_RATE", type=int,
                    default=10,
                    help='Render every nth frame')


parser.add_argument('-rs', '--random-seed', dest="RNG_SEED", type=int,
                    default=0,
                    help='Random Seed')

parser.add_argument('-n', '--noise', dest="NOISE", type=int,
                    default=1,
                    help='Turn noise on/off')

args = parser.parse_args()

RENDER_RATE = args.RENDER_RATE

Vis = args.Vis
PORT1 = args.PORT1
PORT2 = args.PORT2

HOST = '127.0.0.1'   # Symbolic name meaning all available interfaces


random.seed(args.RNG_SEED)

t = time.time()

global score1
global score2
global Total_Ticks

Total_Ticks = 0


global Stochasticity
Stochasticity = args.NOISE
if Stochasticity == 1:
    noise1 = 0.005
    noise2 = 0.01
    noise3 = 2
else:
    noise1 = 0
    noise2 = 0
    noise3 = 0


# Handle exceptions here

# Exception handlers here

timeout_msg = "TIMED OUT"
timeout_period = 0.5


def is_Ended(space):
    for shape in space._get_shapes():
        if abs(shape.body.velocity[0]) > Static_Velocity_Threshold or abs(shape.body.velocity[1]) > Static_Velocity_Threshold:
            return False
    return True


def requestAction(conn1):
    try:
        data = conn1.recv(1024)
    except:
        data = timeout_msg
    finally:
        return data


def sendState(state, conn1):
    try:
        conn1.send(state)
    except socket.error:
        print "Player timeout"

    return True

'''
Play S,A->S'
Input: 
State: {"Black_Locations":[],"White_Locations":[],"Red_Location":[],"Score":0}
Action: [Angle,X,Force] Legal Actions: ? If action is illegal, take random action
Player: 1 or 2
Vis: Visualization? Will be handled later
'''


def Play(State, Player, action):

    global Vis
    pygame.init()
    clock = pygame.time.Clock()

    if Vis == 1:
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
    Holes = init_holes(space)
    # added
    BackGround = Background('use_layout.png', [-30, -30])

    Coins = init_coins(space, State["Black_Locations"], State[
                       "White_Locations"], State["Red_Location"], passthrough)
    # load_image("layout.jpg")
    Striker = init_striker(space, Board_Size / 2 + 10,
                           passthrough, action, Player)

    if Vis == 1:
        draw_options = pymunk.pygame_util.DrawOptions(screen)

    Ticks = 0
    Foul = False
    Pocketed = []

    # print "Force: ",1000-+action[2]*1000
    Queen_Pocketed = False
    Queen_Flag = False
    while 1:
        global score1
        global score2

        if Ticks % RENDER_RATE == 0 and Vis == 1:
            Local_VIS = True
        else:
            Local_VIS = False

        Ticks += 1
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit(0)

        if Local_VIS == 1:
            screen.blit(BackGround.image, BackGround.rect)
            space.debug_draw(draw_options)

        space.step(1 / TIME_STEP)
        # print Striker[0].position
        for hole in Holes:
            if dist(hole.body.position, Striker[0].position) < Hole_Radius - Striker_Radius + (Striker_Radius * 0.75):
                for shape in space._get_shapes():
                    if shape.color == Striker_Color:
                        Foul = True
                        print "Player " + str(Player) + ": Foul, Striker in hole"
                        space.remove(shape, shape.body)
                        break

        for hole in Holes:
            for coin in space._get_shapes():
                if dist(hole.body.position, coin.body.position) < Hole_Radius - Coin_Radius + (Coin_Radius * 0.75):
                    if coin.color == Black_Coin_Color:
                        Score += 1
                        Pocketed.append((coin, coin.body))
                        space.remove(coin, coin.body)
                        if Player == 1:
                            Foul = True
                            print "Foul, Player 1 pocketed black"
                    if coin.color == White_Coin_Color:
                        Score += 1
                        Pocketed.append((coin, coin.body))
                        space.remove(coin, coin.body)
                        if Player == 2:
                            Foul = True
                            print "Foul, Player 2 pocketed white"
                    if coin.color == Red_Coin_Color:
                        # Score+=3
                        Pocketed.append((coin, coin.body))
                        space.remove(coin, coin.body)
                        Queen_Pocketed = True

        if Local_VIS == 1:
            font = pygame.font.Font(None, 25)

            text = font.render("Player 1 Score: " +
                               str(score1), 1, (220, 220, 220))
            screen.blit(text, (Board_Size / 3 + 67, 780, 0, 0))
            text = font.render("Player 2 Score: " +
                               str(score2), 1, (220, 220, 220))
            screen.blit(text, (Board_Size / 3 + 67, 2, 0, 0))
            text = font.render("Time Elapsed: " +
                               str(round(time.time() - t, 2)), 1, (50, 50, 50))
            screen.blit(text, (Board_Size / 3 + 57, 25, 0, 0))

            if Ticks == 1:
                # The length of the line denotes the action
                length = Striker_Radius + action[2] / 500.0
                startpos_x = action[1]
                angle = action[0]
                if Player == 2:
                    startpos_y = 145
                else:
                    startpos_y = Board_Size - 136
                endpos_x = (startpos_x + cos(angle) * length)
                endpos_y = (startpos_y - (length) * sin(angle))
                pygame.draw.line(
                    screen, (50, 255, 50), (endpos_x, endpos_y), (startpos_x, startpos_y), 3)
                pygame.draw.circle(screen, (50, 255, 50),
                                   (int(endpos_x), int(endpos_y)), 5)
            pygame.display.flip()
            if Ticks == 1:
                time.sleep(1)
            clock.tick()

        # Do post processing and return the next State
        if is_Ended(space) or Ticks > TICKS_LIMIT:
            State_new = {"Black_Locations": [],
                         "White_Locations": [], "Red_Location": [], "Score": 0}

            for coin in space._get_shapes():
                if coin.color == Black_Coin_Color:
                    State_new["Black_Locations"].append(coin.body.position)
                if coin.color == White_Coin_Color:
                    State_new["White_Locations"].append(coin.body.position)
                if coin.color == Red_Coin_Color:
                    State_new["Red_Location"].append(coin.body.position)
            if Foul == True:
                for coin in Pocketed:
                    if coin[0].color == Black_Coin_Color:
                        State_new["Black_Locations"].append(ret_pos(State_new))
                        Score -= 1
                    if coin[0].color == White_Coin_Color:
                        State_new["White_Locations"].append(ret_pos(State_new))
                        Score -= 1
                    if coin[0].color == Red_Coin_Color:
                        State_new["Red_Location"].append(ret_pos(State_new))
                        # Score-=3

            if (Queen_Pocketed == True and Foul == False):
                if len(State_new["Black_Locations"]) + len(State_new["White_Locations"]) == 18:
                    print "The queen cannot be the first to be pocketed: Player ", Player
                    State_new["Red_Location"].append(ret_pos(State_new))
                else:
                    if Score - prevScore > 0:
                        Score += 3
                        print "Queen pocketed and covered in one shot"
                    else:
                        Queen_Flag = True

            print "Player " + str(Player) + ": Turn ended in ", Ticks, " Ticks"
            State_new["Score"] = Score
            global Total_Ticks
            Total_Ticks += Ticks

            return State_new, Queen_Flag


def don():
    s1.close()
    conn1.close()

    s2.close()
    conn2.close()
    print "Done, Closing Connection"
    sys.exit()


def transform_state(state):
    t_state = {}
    t_state["White_Locations"] = []
    t_state["Black_Locations"] = []
    t_state["Red_Location"] = []
    t_state["Score"] = state["Score"]
    for pos in state["White_Locations"]:
        t_state["White_Locations"].append((pos[0], 800 - pos[1]))
    for pos in state["Black_Locations"]:
        t_state["Black_Locations"].append((pos[0], 800 - pos[1]))
    for pos in state["Red_Location"]:
        t_state["Red_Location"].append((pos[0], 800 - pos[1]))
    return t_state


def transform_action(action):
    # print "Recieved " , action[0]
    # print "Retuned", 360-action[0]

    return (360 - action[0], action[1], action[2])


def tuplise(s):
    try:
        return (round(float(s[1]), 4), round(float(s[0]), 4), round(float(s[2]), 4))
    except:
        print "Invalid action, Taking Random"
        return (random.random() * 2 * 3.14, random.random(), random.random())
# There is a min force with which you hit the striker: You cant give up
# turn: Ask sir is correct

# SAMIRAN:IMPLEMENT last response of the agents are emplty.. account for
# that also


def validate(action, Player, state):
    # print "Action Recieved: ",action
    angle = action[0]
    position = action[1]
    force = action[2]
    if (angle < -45 or angle > 225) and Player == 1:
        print "Invalid Angle, taking random angle",
        angle = random.randrange(-45, 270)
        print "which is ", angle
    if (angle > 45 and angle < 135) and Player == 2:
        print "Invalid Angle, taking random angle",
        angle = random.randrange(135, 405)
        if angle > 360:
            angle = angle - 360
        print "which is ", angle
    if position < 0 or position > 1:
        print "Invalid position, taking random position"
        position = random.random()

    s = state.copy()
    try:
        del s["Score"]
    except KeyError:
        pass
    x = s.values()
    x = reduce(lambda x, y: x + y, x)

    if force < 0 or force > 1:
        print "Invalid force, taking random position"
        force = random.random()
    global Stochasticity
    if Stochasticity == 1 and Player == 2:
        angle = angle + randrange(-5, 5)
        # if angle<-45:
        #     angle=-45
        # if angle>225:
        #     angle=225
    if Stochasticity == 1 and Player == 1:
        angle = angle + (random.choice([-1, 1]) * gauss(0, noise3))
        # if angle>45:
        #     angle=45
        # if angle<135:
        #     angle=135
    if angle < 0:
        angle = 360 + angle
    angle = angle / 180.0 * 3.14
    position = 170 + \
        (float(max(min(position + gauss(0, noise2), 1), 0)) * (460))
    force = MIN_FORCE + \
        float(max(min(force + gauss(0, noise3), 1), 0)) * MAX_FORCE

    if Player == 1:
        check = 0
        fuse = 10
        while check == 0 and fuse > 0:
            fuse -= 1
            check = 1

            for i in x:
                if dist((position, 145), i) < Striker_Radius + Coin_Radius:
                    check = 0
                    print "Position ", (position, 145), " clashing with a coin, taking random"
                    position = 170 + \
                        (float(max(min(float(random.random()) + gauss(0, noise1), 1), 0)) * (460))
    if Player == 2:
        check = 0
        fuse = 10
        while check == 0 and fuse > 0:
            fuse -= 1
            check = 1

            for i in x:
                if dist((position, Board_Size - 136), i) < Striker_Radius + Coin_Radius:
                    check = 0
                    print "Position ", (position, 145), " clashing with a coin, taking random"
                    position = 170 + \
                        (float(max(min(float(random.random()) + gauss(0, noise1), 1), 0)) * (460))

    action = (angle, position, force)
    # print "Final action", action
    return action

if __name__ == '__main__':

    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s1.bind((HOST, PORT1))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    s1.listen(1)
    conn1, addr1 = s1.accept()
    conn1.settimeout(timeout_period)

    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s2.bind((HOST, PORT2))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    s2.listen(1)
    conn2, addr2 = s2.accept()
    conn2.settimeout(timeout_period)

    global score1
    global score2

    winner = 0
    reward1 = 0
    score1 = 0
    reward2 = 0
    score2 = 0

    State = {'White_Locations': [(400, 368), (437, 420), (372, 428), (337, 367), (402, 332), (463, 367), (470, 437), (405, 474), (340, 443)], 'Red_Location': [(
        400, 403)], 'Score': 0, 'Black_Locations': [(433, 385), (405, 437), (365, 390), (370, 350), (432, 350), (467, 402), (437, 455), (370, 465), (335, 406)]}
    next_State = State

    it = 1

    while it < 200:  # Number of Chances given to each player

        it += 1

        prevScore = next_State["Score"]
        sendState(str(next_State) + ";REWARD" + str(reward1), conn1)
        s = requestAction(conn1)
        if not s:  # response empty
            print "No response from player 1"
            winner = 2
            break
        elif s == timeout_msg:
            print "Timeout from player 1"
            winner = 2
            break
        else:
            action = tuplise(s.replace(" ", "").split(','))
        next_State, Queen_Flag = Play(
            next_State, 1, validate(action, 1, next_State))
        print "Coins: ", len(next_State["Black_Locations"]), "B ", len(next_State["White_Locations"]), "W ", len(next_State["Red_Location"]), "R"

        reward1 = next_State["Score"] - prevScore
        prevScore = next_State["Score"]
        score1 = score1 + reward1
        while Queen_Flag or reward1 > 0 and (len(next_State["Black_Locations"]) != 0 and len(next_State["White_Locations"]) != 0):
            if Queen_Flag == 1:
                print "Pocketed Queen, pocket any coin in this turn to cover it"
            prevScore = next_State["Score"]

            sendState(str(next_State) + ";REWARD" + str(reward1), conn1)
            s = requestAction(conn1)
            if not s:  # response empty
                print "No response from player 1"
                winner = 2
                break
            elif s == timeout_msg:
                print "Timeout from player 1"
                winner = 2
                break
            else:
                action = tuplise(s.replace(" ", "").split(','))
            old_Queen_Flag = Queen_Flag
            next_State, Queen_Flag = Play(
                next_State, 1, validate(action, 1, next_State))
            print "Coins: ", len(next_State["Black_Locations"]), "B ", len(next_State["White_Locations"]), "W ", len(next_State["Red_Location"]), "R"

            reward1 = next_State["Score"] - prevScore
            if old_Queen_Flag == 1:
                if reward1 > 0:
                    score1 += 3
                    print "Sucessfully covered the queen"
                else:
                    print "Could not cover the queen"
                    next_State["Red_Location"].append(ret_pos(next_State))
            prevScore = next_State["Score"]
            score1 = score1 + reward1
            if len(next_State["Black_Locations"]) == 0 or len(next_State["White_Locations"]) == 0:
                break


# Add authors
        if len(next_State["Black_Locations"]) == 0 or len(next_State["White_Locations"]) == 0:
            break

        sendState(str(transform_state(next_State)) +
                  ";REWARD" + str(reward2), conn2)
        s = requestAction(conn2)
        if not s:  # response empty
            print "No response from Player 2"
            winner = 1
            break
        elif s == timeout_msg:
            print "Timeout from Player 2"
            winner = 1
            break
        else:
            action = transform_action(tuplise(s.replace(" ", "").split(',')))

        next_State, Queen_Flag = Play(
            next_State, 2, validate(action, 2, next_State))
        print "Coins: ", len(next_State["Black_Locations"]), "B ", len(next_State["White_Locations"]), "W ", len(next_State["Red_Location"]), "R"

        reward2 = next_State["Score"] - prevScore
        score2 = score2 + reward2
        while Queen_Flag or reward2 > 0 and (len(next_State["Black_Locations"]) != 0 and len(next_State["White_Locations"]) != 0):

            prevScore = next_State["Score"]
            if Queen_Flag == 1:
                print "Pocketed Queen, pocket any coin in this turn to cover it"
            sendState(str(transform_state(next_State)) +
                      ";REWARD" + str(reward2), conn2)
            s = requestAction(conn2)
            if not s:  # response empty
                print "No response from Player 2"
                winner = 1
                break
            elif s == timeout_msg:
                print "Timeout from Player 2"
                winner = 1
                break
            else:
                action = transform_action(
                    tuplise(s.replace(" ", "").split(',')))
            old_Queen_Flag = Queen_Flag
            next_State, Queen_Flag = Play(
                next_State, 2, validate(action, 2, next_State))
            print "Coins: ", len(next_State["Black_Locations"]), "B ", len(next_State["White_Locations"]), "W ", len(next_State["Red_Location"]), "R"

            reward2 = next_State["Score"] - prevScore
            if old_Queen_Flag == 1:

                if reward2 > 0:
                    score2 += 3
                    print "Successfully covered the queen"
                else:
                    print "Could not cover the queen"
                    next_State["Red_Location"].append(ret_pos(next_State))
            score2 = score2 + reward2
            if len(next_State["Black_Locations"]) == 0 or len(next_State["White_Locations"]) == 0:
                break

        print "P1 score: ", score1, " P2 score: ", score2, " Turn " + str(it)
        print "Coins: ", len(next_State["Black_Locations"]), "B ", len(next_State["White_Locations"]), "W ", len(next_State["Red_Location"]), "R"
        if len(next_State["Black_Locations"]) == 0 or len(next_State["White_Locations"]) == 0:
            break

    if winner == 2:
        print "Player 1 Timeout"
    elif winner == 1:
        print "Player 2 Timeout"
    if winner == 0:
        if len(next_State["White_Locations"]) == 0:
            if len(next_State["Red_Location"]) > 0:
                winner = 2
            else:
                winner = 1
            msg = "Winner is Player " + str(winner)
        elif len(next_State["Black_Locations"]) == 0:
            if len(next_State["Red_Location"]) > 0:
                winner = 1
            else:
                winner = 2
            msg = "Winner is Player " + str(winner)
        else:
            msg = "Draw"

    f = open("S2_log", "a")
    f.write(str(it) + " " + str(round(time.time() - t, 0)) + " " +
            str(winner) + " " + str(score1) + " " + str(score2) + "\n")
    f.close()
    don()

# Generate Traces and report any inconsistencies
