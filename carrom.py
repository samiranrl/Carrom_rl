from Utils import *
import time
t=time.time()
def is_Ended(space, Striker, Coins):
    for coin in space._get_shapes():
        if coin.body.velocity[0]>Static_Velocity_Threshold or coin.body.velocity[1]>Static_Velocity_Threshold:
            return False
    return True

def Play(State,Vis,Flip,action):
    
    pygame.init()
    clock = pygame.time.Clock()
    if Vis==1:
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
    Coins=init_coins(space,State["Black_Locations"],State["White_Locations"],State["Red_Location"],passthrough)
    Holes=init_holes(space)
    Striker=init_striker(space,Board_Size/2+10, passthrough,action)
        
    if Vis==1:
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

        if Vis==1:

            screen.fill(Board_Color)



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







        space.step(1/10.0)







        #print space.shapes[1]

        if Vis==1:
            font = pygame.font.Font(None, 25)
            text = font.render("SCORE: "+str(Score)+"  FPS: "+str(int(clock.get_fps()))+" REALTIME :"+ str(round(time.time()-t,2)) + "s", 1, (10, 10, 10))
            screen.blit(text, (0,Board_Size/10,0,0))
            pygame.display.flip()
            clock.tick()




        # Do post processing and return the next State

        if is_Ended(space,Striker,Coins):

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




    

if __name__ == '__main__':
    B=generate_coin_locations(9)

    W=generate_coin_locations(9)

    R=generate_coin_locations(1)
    State={"Black_Locations":B,"White_Locations":W,"Red_Location":R,"Score":0}

    # Black Coins, White Coins, Red Coin, Visualization : On/Off, Score, Flip the board? 0 - no 1 - yes
    action=(random.random()*6.28,(random.randrange(Board_Size/10,Board_Size-Board_Size/10),100), random.randrange(100,10000))
    next_State=Play(State,1,0,action)
    it=1
    while 1:
        action=(random.random()*6.28,(random.randrange(Board_Size/10,Board_Size-Board_Size/10),100), random.randrange(100,5000))
        
        next_State=Play(next_State,1,0,action)
        print len(next_State["Black_Locations"]),len(next_State["White_Locations"]),len(next_State["Red_Location"])
        print "step"+str(it)
        it+=1

