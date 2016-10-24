from Utils import *
from thread import *
from math import pi
import time
import sys
import os
import argparse
import socket

start_time = time.time()

# Parse arguments

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--visualization', dest="vis", type=int,
                    default=0,
                    help='visualization on/off')

parser.add_argument('-rr', '--', dest="render_rate", type=int,
                    default=10,
                    help='Render every nth frame')

parser.add_argument('-p', '--port', dest="port1", type=int,
                    default=12121,
                    help='Port for incoming connection')

parser.add_argument('-rs', '--random-seed', dest="rng", type=int,
                    default=0,
                    help='Random Seed')

parser.add_argument('-n', '--noise', dest="noise", type=int,
                    default=1,
                    help='Turn noise on/off')

parser.add_argument('-log', '--log', dest="log", type=str,
                    default="log1",
                    help='Name of logfile')

args = parser.parse_args()

log = args.log
render_rate = args.render_rate
vis = args.vis
port1 = args.port1
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

# Play one step of carrom
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
    score = state["Score"]
    prevscore = state["Score"]

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

    striker = init_striker(space, BOARD_SIZE / 2 + 10,
                           passthrough, action, player)

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

        # Remove pocketed striker

        for pocket in pockets:
            if dist(pocket.body.position, striker[0].position) < POCKET_RADIUS - STRIKER_RADIUS + (STRIKER_RADIUS * 0.75):
                foul = True
                for shape in space._get_shapes():
                    if shape.color == STRIKER_COLOR:
                        space.remove(shape, shape.body)
                        break
        # Remove pocketed coins

        for pocket in pockets:
            for coin in space._get_shapes():
                if dist(pocket.body.position, coin.body.position) < POCKET_RADIUS - COIN_RADIUS + (COIN_RADIUS * 0.75):
                    if coin.color == BLACK_COIN_COLOR:
                        score += 1
                        pocketed.append((coin, coin.body))
                        space.remove(coin, coin.body)
                    if coin.color == WHITE_COIN_COLOR:
                        score += 1
                        pocketed.append((coin, coin.body))
                        space.remove(coin, coin.body)
                    if coin.color == RED_COIN_COLOR:
                        pocketed.append((coin, coin.body))
                        space.remove(coin, coin.body)
                        queen_pocketed = True

        if local_vis == 1:
            font = pygame.font.Font(None, 25)
            text = font.render("Score: " +
                               str(score), 1, (220, 220, 220))
            screen.blit(text, (BOARD_SIZE / 2 - 40, 780, 0, 0))

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

            if len(state_new["Black_Locations"]) == 0 and len(state_new["White_Locations"]) == 0:
                if len(state_new["Red_Location"]) > 0:
                    state_new["Black_Locations"].append(ret_pos(state_new))
                    score -= 1
                    print "Failed to clear queen, getting another turn"

            state_new["Score"] = score
            print "Coins Remaining: ", len(state_new["Black_Locations"]), "B ", len(state_new["White_Locations"]), "W ", len(state_new["Red_Location"]), "R"
            return state_new, queen_flag, score-prevscore


# Validate parsed action

def validate(action, state):
    print "Server received action: ", action
    position = action[0]
    angle = action[1]
    force = action[2]
    if angle < -45 or angle > 225:
        print "Invalid Angle, taking random angle",
        angle = random.randrange(-45, 225)
        print "which is ", angle
    if position < 0 or position > 1:
        print "Invalid position, taking random position"
        position = random.random()
    if force < 0 or force > 1:
        print "Invalid force, taking random position"
        force = random.random()

    angle = angle + (random.choice([-1, 1]) * gauss(0, noise3))
    if angle < -45:
        angle = -45
    if angle > 225:
        angle = 225

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

    while check == 0 and fuse > 0:
        fuse -= 1
        check = 1
        for coin in tmp_state:
            # print coin, dist((position, 145), coin)
            if dist((position, 145), coin) < STRIKER_RADIUS + COIN_RADIUS:
                check = 0
                # print "Position ", (position, 145), " clashing with a coin,
                # taking random"
                position = random.randrange(170, 630)
                # print "checking", position

    # print "Final action", action
    action = (position, angle, force)
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

    winner = 0
    reward = 0
    score1 = 0

    state = INITIAL_STATE
    next_state = state

    it = 0

    while it < 500:  # Number of chances given to the player
        it += 1
        # print "Sending ", next_state
        send_state(str(next_state) + ";REWARD" + str(reward), conn1)
        s = request_action(conn1)
        if not s:  # response empty
            print "No response from player 1, aborting"
            logger(log, "No response from player 1, aborting\n")
            sys.exit()
        elif s == timeout_msg:
            print "Player 1 timeout, aborting"
            logger(log, "Player 1 timeout, aborting\n")
            sys.exit()
        else:
            action = tuplise(s.replace(" ", "").split(','))

        next_state, queen_flag, reward = play(
            next_state, 1, validate(action, next_state))

        score1 += reward
        print "turn: " + str(it) + " score: " + str(score1)
        while queen_flag:  # Extra turn to cover queen
            print "Pocketed Queen, pocket any coin in this turn to cover it"
            it += 1

            send_state(str(next_state) + ";REWARD" + str(reward), conn1)
            s = request_action(conn1)
            if not s:  # response empty
                print "No response from player 1, aborting"
                logger(log, "No response from player 1, aborting\n")
                sys.exit()
            elif s == timeout_msg:
                print "Player 1 timeout, aborting"
                logger(log, "Player 1 timeout, aborting\n")
                sys.exit()
            else:
                action = tuplise(s.replace(" ", "").split(','))
            next_state, queen_flag, reward = play(
                next_state, 1, validate(action, next_state))
            if reward > 0:
                # print "Reward > 0, is the score updated?
                # ",next_state["Score"]
                next_state["Score"] += 3
                reward += 3
                # print "Reward > 0, is the score updated?
                # ",next_state["Score"]
                print "Successfully covered the queen"
            else:
                print "Could not cover the queen"
                next_state["Red_Location"].append(ret_pos(next_state))
            score1 += reward
            print "Score: ", score1, " turns: " + str(it)
        if len(next_state["Black_Locations"]) + len(next_state["White_Locations"]) + len(next_state["Red_Location"]) == 0:
            print "Cleared Board in " + str(it) + " turns. Realtime taken: "+str(time.time(
            ) - start_time)+" s @ "+str(round((it*1.0)/(time.time() - start_time), 2)) + " turns/s\n"
            break

    if it >= 500:
        logger(log, "Player took more than 500 turns, aborting\n")
        print "Player took more than 500 turns, aborting"
        sys.exit()

    tmp = "Cleared Board in " + str(it) + " turns. Realtime taken: "+str(time.time(
    ) - start_time)+" s @ "+str(round((it*1.0)/(time.time() - start_time), 2)) + " turns/s\n"
    logger(log, tmp)
    don(s1, conn1)
