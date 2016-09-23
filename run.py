import pickle
import pygame
import pymunk.pygame_util
import pymunk
zzz = pickle.load( open( "dump.p", "rb" ) )
import cv2
print len(zzz)
pygame.init()
screen = pygame.display.set_mode((800,800))
print type(screen)
pygame.display.set_caption('Visualization of the Game') #Our game's name is Somnium!
clock = pygame.time.Clock()
for i in zzz:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()
	image=pygame.image.fromstring(i, (800,800), "RGB")
	screen.blit(image,(0,0))
	pygame.display.flip()
	clock.tick(20)

