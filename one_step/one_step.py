
# one step simulation function

from Utils import *
from thread import *
from math import pi
import time


noise = 1
if noise == 1:
    noise1 = 0.005
    noise2 = 0.01
    noise3 = 2
else:
    noise1 = 0
    noise2 = 0
    noise3 = 0


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




def simulate(state, action):
    pygame.init()
    clock = pygame.time.Clock()

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
    #background = BACKGROUND('use_layout.png', [-30, -30])

    coins = init_coins(space, state["Black_Locations"], state[
                       "White_Locations"], state["Red_Location"], passthrough)

    striker = init_striker(space, BOARD_SIZE / 2 + 10,
                           passthrough, action, 1)

    ticks = 0
    foul = False
    pocketed = []
    queen_pocketed = False
    queen_flag = False

    while 1:

        ticks += 1

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

            state_new["Score"] = score
            # print "Coins Remaining: ", len(state_new["Black_Locations"]), "B
            # ", len(state_new["White_Locations"]), "W ",
            # len(state_new["Red_Location"]), "R"
            return state_new, score-prevscore


if __name__ == "__main__":
    state = INITIAL_STATE
    next_state, reward = simulate(state,validate([0.5, 90, 0.5],state))
    print reward
