import pygame

from pygame.locals import *

pygame.init()

running = True

screen = pygame.display.set_mode((640,480))

clock = pygame.time.Clock()

while running:
	clock.tick(7)
