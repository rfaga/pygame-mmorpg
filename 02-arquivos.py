import pygame, cPickle
from pygame.locals import *

tilemap = cPickle.load(file('data/tilemap.txt'))

objmap = cPickle.load(file('data/objmap.txt'))

running = True
screen = pygame.display.set_mode((640,480))
clock = pygame.time.Clock()

while running:
	clock.tick(7)
