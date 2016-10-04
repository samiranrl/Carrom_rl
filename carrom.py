from Utils import *
import time,pickle
t=time.time()


def is_Ended(space, Striker, Coins):
    for coin in space._get_shapes():
        if abs(coin.body.velocity[0])>Static_Velocity_Threshold or abs(coin.body.velocity[1])>Static_Velocity_Threshold:
            return False
    if abs(Striker.body.velocity[0]>Static_Velocity_Threshold) or abs(Striker.body.velocity[1])>Static_Velocity_Threshold:
        return False
    return True

'''
Play S,A->S'
Input: 
State: {"Black_Locations":[],"White_Locations":[],"Red_Location":[],"Score":0}
Action: [Angle,X,Force] Legal Actions: ? If action is illegal, take random action
Player: 1 or 2
Vis: Visualization? Will be handled later
'''

def Play(State,Vis,Player,action):
    
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
    Holes=init_holes(space)
    ##added
    BackGround = Background('use_layout.png', [-30,-30])

    Coins=init_coins(space,State["Black_Locations"],State["White_Locations"],State["Red_Location"],passthrough)
    #load_image("layout.jpg")
    Striker=init_striker(space,Board_Size/2+10, passthrough,action, Player)
        
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

            #screen.fill(Board_Color)
            screen.fill([255, 255, 255])
            screen.blit(BackGround.image, BackGround.rect)
            space.debug_draw(draw_options)
        if Ticks%100==0:
            pass
            #print pygame.image.tostring(screen,"RGB")
        
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
            screen.blit(text, (20,Board_Size/10,0,0))
            pygame.display.flip()
            clock.tick(100)




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






if __name__ == '__main__':
    B=generate_coin_locations(9)

    W=generate_coin_locations(9)

    R=generate_coin_locations(1)
    State={"Black_Locations":B,"White_Locations":W,"Red_Location":R,"Score":0}

    # Black Coins, White Coins, Red Coin, Visualization : On/Off, Score, Flip the board? 0 - no 1 - yes
    action=(0,400, random.randrange(1000,10000))
    next_State=Play(State,1,2,action)
    it=1
    States=[]
    while it<5000:
        #action=(random.random()*6.28,random.randrange(170,630), random.randrange(1000,10000))
        action=(0,400, random.randrange(1000,10000))
        next_State=Play(next_State,1,2,action)
 
        print len(next_State["Black_Locations"]),len(next_State["White_Locations"]),len(next_State["Red_Location"])
        print "step"+str(it)
        it+=1
