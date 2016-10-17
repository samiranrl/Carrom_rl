
# one step simulation function

from Utils import *
from thread import *
from math import pi
import time


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
                Foul = True
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
                        Score -= 1
                    if coin[0].color == WHITE_COIN_COLOR:
                        state_new["White_Locations"].append(ret_pos(state_new))
                        Score -= 1
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
    next_state, reward = simulate(state, [0.1, 200, 0.5])
    print reward
