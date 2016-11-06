from Utils import *
from thread import *
from math import pi
import time
import sys
import os
import argparse
import socket

start_time = time.time()


parser = argparse.ArgumentParser()

parser.add_argument('-v', '--visualization', dest="vis", type=int,
                    default=0,
                    help='visualization on/off')

parser.add_argument('-rr', '--', dest="render_rate", type=int,
                    default=10,
                    help='Render every nth frame')

parser.add_argument('-p1', '--port1', dest="port1", type=int,
                    default=12121,
                    help='Port for incoming connection')

parser.add_argument('-p2', '--port2', dest="port2", type=int,
                    default=34343,
                    help='Port for incoming connection')

parser.add_argument('-rs', '--random-seed', dest="rng", type=int,
                    default=0,
                    help='Random Seed')

parser.add_argument('-n', '--noise', dest="noise", type=int,
                    default=1,
                    help='Turn noise on/off')

parser.add_argument('-log', '--log', dest="log", type=str,
                    default="log2",
                    help='Name of logfile')

args = parser.parse_args()


log = args.log
render_rate = args.render_rate
vis = args.vis
port1 = args.port1
port2 = args.port2
random.seed(args.rng)

host = '127.0.0.1'   # Symbolic name meaning all available interfaces

noise = args.noise
if noise == 1:
    noise1 = 0.005
    noise2 = 0.01
    noise3 = 2
else:
    noise1 = 0
    noise2 = 0
    noise3 = 0

timeout_msg = "TIMED OUT"
timeout_period = 0.5


##########################################################################

# play one step of carrom
# Input: state, player, action
# Output: next_state, queen_flag, reward
# queen_flag denotes that the queen is pocketed and must be covered in the
# next turn


def play(state, player, action):
    pygame.init()
    clock = pygame.time.Clock()

    if vis == 1:
        screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
        pygame.display.set_caption("Carrom RL Simulation")

    space = pymunk.Space(threaded=True)
    if player == 1:
        global score1
        score = score1
        prevscore = score1

    if player == 2:
        global score2
        score = score2
        prevscore = score2

    # pass through object // Dummy Object for handling collisions
    passthrough = pymunk.Segment(space.static_body, (0, 0), (0, 0), 5)
    passthrough.collision_type = 2
    passthrough.filter = pymunk.ShapeFilter(categories=0b1000)

    init_space(space)
    init_walls(space)
    pockets = init_pockets(space)
    background = BACKGROUND('use_layout.png', [-30, -30])

    coins = init_coins(space, state["Black_Locations"], state[
                       "White_Locations"], state["Red_Location"], passthrough)

    striker = init_striker(space, passthrough, action, player)

    if vis == 1:
        draw_options = pymunk.pygame_util.DrawOptions(screen)

    ticks = 0
    foul = False
    pocketed = []
    queen_pocketed = False
    queen_flag = False

    while 1:

        if ticks % render_rate == 0 and vis == 1:
            local_vis = True
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    sys.exit(0)
        else:
            local_vis = False

        ticks += 1

        if local_vis == 1:
            screen.blit(background.image, background.rect)
            space.debug_draw(draw_options)

        space.step(1 / TIME_STEP)

        for pocket in pockets:
            if dist(pocket.body.position, striker[0].position) < POCKET_RADIUS - STRIKER_RADIUS + (STRIKER_RADIUS * 0.75):
                foul = True
                for shape in space._get_shapes():
                    if shape.color == STRIKER_COLOR:
                        print "player " + str(player) + ": Foul, Striker pocketed"
                        space.remove(shape, shape.body)
                        break

        for pocket in pockets:
            for coin in space._get_shapes():
                if dist(pocket.body.position, coin.body.position) < POCKET_RADIUS - COIN_RADIUS + (COIN_RADIUS * 0.75):
                    if coin.color == BLACK_COIN_COLOR:
                        score += 1
                        pocketed.append((coin, coin.body))
                        space.remove(coin, coin.body)
                        if player == 1:
                            foul = True
                            print "Foul, player 1 pocketed black"
                    if coin.color == WHITE_COIN_COLOR:
                        score += 1
                        pocketed.append((coin, coin.body))
                        space.remove(coin, coin.body)
                        if player == 2:
                            foul = True
                            print "Foul, player 2 pocketed white"
                    if coin.color == RED_COIN_COLOR:
                        pocketed.append((coin, coin.body))
                        space.remove(coin, coin.body)
                        queen_pocketed = True

        if local_vis == 1:
            font = pygame.font.Font(None, 25)

            text = font.render("player 1 Score: " +
                               str(score1), 1, (220, 220, 220))
            screen.blit(text, (BOARD_SIZE / 3 + 67, 780, 0, 0))
            text = font.render("player 2 Score: " +
                               str(score2), 1, (220, 220, 220))
            screen.blit(text, (BOARD_SIZE / 3 + 67, 2, 0, 0))
            text = font.render("Time Elapsed: " +
                               str(round(time.time() - start_time, 2)), 1, (50, 50, 50))
            screen.blit(text, (BOARD_SIZE / 3 + 57, 25, 0, 0))

            # First tick, draw an arrow representing action

            if ticks == 1:
                force = action[2]
                angle = action[1]
                position = action[0]
                draw_arrow(screen, position, angle, force, player)

            pygame.display.flip()
            if ticks == 1:
                time.sleep(1)

            clock.tick()

        # Do post processing and return the next State
        if is_ended(space) or ticks > TICKS_LIMIT:
            state_new = {"Black_Locations": [],
                         "White_Locations": [], "Red_Location": [], "Score": 0}

            for coin in space._get_shapes():
                if coin.color == BLACK_COIN_COLOR:
                    state_new["Black_Locations"].append(coin.body.position)
                if coin.color == WHITE_COIN_COLOR:
                    state_new["White_Locations"].append(coin.body.position)
                if coin.color == RED_COIN_COLOR:
                    state_new["Red_Location"].append(coin.body.position)

            if foul == True:
                print "Foul.. striker pocketed"
                for coin in pocketed:
                    if coin[0].color == BLACK_COIN_COLOR:
                        state_new["Black_Locations"].append(ret_pos(state_new))
                        score -= 1
                    if coin[0].color == WHITE_COIN_COLOR:
                        state_new["White_Locations"].append(ret_pos(state_new))
                        score -= 1
                    if coin[0].color == RED_COIN_COLOR:
                        state_new["Red_Location"].append(ret_pos(state_new))

            if (queen_pocketed == True and foul == False):
                if len(state_new["Black_Locations"]) + len(state_new["White_Locations"]) == 18:
                    print "The queen cannot be the first to be pocketed: player ", player
                    state_new["Red_Location"].append(ret_pos(state_new))
                else:
                    if score - prevscore > 0:
                        score += 3
                        print "Queen pocketed and covered in one shot"
                    else:
                        queen_flag = True

            print "player " + str(player) + ": Turn ended in ", ticks, " Ticks"
            state_new["Score"] = score
            print "Coins Remaining: ", len(state_new["Black_Locations"]), "B ", len(state_new["White_Locations"]), "W ", len(state_new["Red_Location"]), "R"
            return state_new, queen_flag, score-prevscore


def validate(action, player, state):
    # print "Action Received", action

    position = action[0]
    angle = action[1]
    force = action[2]

    if (angle < -45 or angle > 225) and player == 1:
        print "Invalid angle, taking random angle",
        angle = random.randrange(-45, 225)
        print "which is ", angle

    if (angle > 45 and angle < 135) and player == 2:
        print "Invalid angle, taking random angle",
        angle = random.randrange(135, 405)
        if angle > 360:
            angle = angle - 360
        print "which is ", angle

    if position < 0 or position > 1:
        print "Invalid position, taking random position"
        position = random.random()

    if force < 0 or force > 1:
        print "Invalid force, taking random position"
        force = random.random()

    angle = angle + (random.choice([-1, 1]) * gauss(0, noise3))

    if angle < 0:
        angle = 360 + angle
    angle = angle / 180.0 * pi
    position = 170 + \
        (float(max(min(position + gauss(0, noise1), 1), 0)) * (460))
    force = MIN_FORCE + \
        float(max(min(force + gauss(0, noise2), 1), 0)) * MAX_FORCE

    tmp_state = state.copy()

    try:
        del tmp_state["Score"]
    except KeyError:
        pass
    tmp_state = tmp_state.values()
    tmp_state = reduce(lambda x, y: x + y, tmp_state)

    check = 0
    fuse = 10

    if player == 1:
        check = 0
        fuse = 10
        while check == 0 and fuse > 0:
            fuse -= 1
            check = 1

            for coin in tmp_state:
                if dist((position, 140), coin) < STRIKER_RADIUS + COIN_RADIUS:
                    check = 0
                    print "Position ", (position, 140), " clashing with a coin, taking random"
                    position = 170 + \
                        (float(
                            max(min(float(random.random()) + gauss(0, noise1), 1), 0)) * (460))

    if player == 2:
        check = 0
        fuse = 10
        while check == 0 and fuse > 0:
            fuse -= 1
            check = 1

            for coin in tmp_state:
                if dist((position, BOARD_SIZE - 140), coin) < STRIKER_RADIUS + COIN_RADIUS:
                    check = 0
                    print "Position ", (position, 140), " clashing with a coin, taking random"
                    position = 170 + \
                        (float(
                            max(min(float(random.random()) + gauss(0, noise1), 1), 0)) * (460))

    action = (position, angle, force)
    # print "Final action", action
    return action

# Generate logs


def logger(log, msg):
    f = open("logs/"+log, "a")
    f.write(msg)
    f.close()


# The server receives an action from the agent
def request_action(conn1):
    try:
        data = conn1.recv(1024)
    except:
        data = timeout_msg
    finally:
        return data

# The server sends it's state to the agent


def send_state(state, conn1):
    try:
        conn1.send(state)
    except socket.error:
        print "Aborting, player did not respond within timeout"
        logger(log, "Aborting, player did not respond within timeout\n")
        sys.exit()
    return True


if __name__ == '__main__':

    # Bind to socket, and wait for the agent to connect
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s1.bind((host, port1))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    s1.listen(1)
    conn1, addr1 = s1.accept()
    conn1.settimeout(timeout_period)

    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s2.bind((host, port2))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    s2.listen(1)
    conn2, addr2 = s2.accept()
    conn2.settimeout(timeout_period)

    winner = 0
    reward1 = 0
    score1 = 0
    reward2 = 0
    score2 = 0

    next_state = INITIAL_STATE

    it = 1

    while it < 200:  # Number of Chances given to each player

        it += 1

        send_state(str(next_state) + ";REWARD" + str(reward1), conn1)
        s = request_action(conn1)
        if not s:  # response empty
            print "No response from player 1"
            logger(log, "No response from player 1, aborting\n")
            winner = 2
            break
        elif s == timeout_msg:
            print "Timeout from player 1"
            logger(log, "player 1 timeout, aborting\n")
            winner = 2
            break
        else:
            action = tuplise(s.replace(" ", "").split(','))
        next_state, queen_flag, reward1 = play(
            next_state, 1, validate(action, 1, next_state))
        score1 = score1 + reward1

        while queen_flag or reward1 > 0 and (len(next_state["Black_Locations"]) != 0 and len(next_state["White_Locations"]) != 0):
            if queen_flag == 1:
                print "Pocketed Queen, pocket any coin in this turn to cover it"

            send_state(str(next_state) + ";REWARD" + str(reward1), conn1)
            s = request_action(conn1)
            if not s:  # response empty
                print "No response from player 1, aborting"
                logger(log, "No response from player 1, aborting\n")
                winner = 2
                break
            elif s == timeout_msg:
                print "player 1 timeout, aborting"
                logger(log, "player 1 timeout, aborting\n")
                winner = 2
                break
            else:
                action = tuplise(s.replace(" ", "").split(','))
            old_queen_flag = queen_flag
            next_state, queen_flag, reward1 = play(
                next_state, 1, validate(action, 1, next_state))

            if old_queen_flag == 1:
                if reward1 > 0:
                    score1 += 3
                    print "Sucessfully covered the queen"
                else:
                    print "Could not cover the queen"
                    next_state["Red_Location"].append(ret_pos(next_state))
            score1 = score1 + reward1

        if len(next_state["Black_Locations"]) == 0 or len(next_state["White_Locations"]) == 0:
            break

        send_state(str(transform_state(next_state)) +
                   ";REWARD" + str(reward2), conn2)

        s = request_action(conn2)
        if not s:  # response empty
            print "No response from player 2"
            logger(log, "No response from player 2, aborting\n")
            winner = 1
            break
        elif s == timeout_msg:
            print "Timeout from player 2"
            logger(log, "player 2 timeout, aborting\n")
            winner = 1
            break
        else:
            action = transform_action(tuplise(s.replace(" ", "").split(',')))

        next_state, queen_flag, reward2 = play(
            next_state, 2, validate(action, 2, next_state))

        score2 = score2 + reward2
        while queen_flag or reward2 > 0 and (len(next_state["Black_Locations"]) != 0 and len(next_state["White_Locations"]) != 0):

            if queen_flag == 1:
                print "Pocketed Queen, pocket any coin in this turn to cover it"
            send_state(str(transform_state(next_state)) +
                       ";REWARD" + str(reward2), conn2)
            s = request_action(conn2)
            if not s:  # response empty
                print "No response from player 2"
                logger(log, "No response from player 2, aborting\n")
                winner = 1
                break
            elif s == timeout_msg:
                print "Timeout from player 2"
                logger(log, "player 2 timeout, aborting\n")
                winner = 1
                break
            else:
                action = transform_action(
                    tuplise(s.replace(" ", "").split(',')))
            old_queen_flag = queen_flag
            next_state, queen_flag, reward2 = play(
                next_state, 2, validate(action, 2, next_state))

            if old_queen_flag == 1:

                if reward2 > 0:
                    score2 += 3
                    print "Successfully covered the queen"
                else:
                    print "Could not cover the queen"
                    next_state["Red_Location"].append(ret_pos(next_state))

            score2 = score2 + reward2
            if len(next_state["Black_Locations"]) == 0 or len(next_state["White_Locations"]) == 0:
                break

        print "P1 score: ", score1, " P2 score: ", score2, " Turn " + str(it)
        print "Coins: ", len(next_state["Black_Locations"]), "B ", len(next_state["White_Locations"]), "W ", len(next_state["Red_Location"]), "R"
        if len(next_state["Black_Locations"]) == 0 or len(next_state["White_Locations"]) == 0:
            break

    if winner == 2:
        print "player 1 Timeout"
    elif winner == 1:
        print "player 2 Timeout"
    if winner == 0:
        if len(next_state["White_Locations"]) == 0:
            if len(next_state["Red_Location"]) > 0:
                winner = 2
            else:
                winner = 1
            msg = "Winner is player " + str(winner)
        elif len(next_state["Black_Locations"]) == 0:
            if len(next_state["Red_Location"]) > 0:
                winner = 1
            else:
                winner = 2
            msg = "Winner is player " + str(winner)
        else:
            msg = "Draw"
    print msg
    msg += " , "+str(round(time.time() - start_time, 2)) + " s time taken\n"
    logger(log, msg)
    don(s1, conn1)
    don(s2, conn2)
