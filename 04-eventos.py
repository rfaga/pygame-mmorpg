import pygame, cPickle
from pygame.locals import *

from pygame.event import Event


tilemap = cPickle.load(file('data/tilemap.txt'))
objmap = cPickle.load(file('data/objmap.txt'))
running = True
screen = pygame.display.set_mode((640,480))
clock = pygame.time.Clock()

#eventos definidos por voce!
GOTO = 24
MESSAGE = 25
SETOBJECT = 26
SYSTEM = 27
GETINFO = 28

WIDTH, HEIGHT, TILE = 16, 12, 40

MIDDLE = WIDTH/2 - 1 , HEIGHT/2 - 1

tile, obj = [], []

for i in range(24):
	tile += [pygame.image.load('imagens/tile%s.png'%i)]
	obj += [pygame.image.load('imagens/obj%s.png'%i)]
	

# Manipulando movimento, teclado e eventos

slide_x = 0
slide_y = 0

def goto(x, y):
	global slide_x, slide_y
	slide_x = x - MIDDLE[0]
	slide_y = y - MIDDLE[1]
	pygame.display.set_caption("MMORPG Client - Pos: %2d, %2d"%(x, y))

def move((inc_x, inc_y)):
	if inc_x != 0 or inc_y != 0:
		e = Event(GOTO, {'x': slide_x + inc_x + MIDDLE[0], 'y': slide_y + inc_y + MIDDLE[1]})
		pygame.event.post(e)

MOVES = {
K_RIGHT: ( 1, 0),
K_LEFT : (-1, 0),
K_UP   : ( 0,-1),
K_DOWN : ( 0, 1)
}

moving = (0,0)
def handle():
	global running, moving
	for e in pygame.event.get():
		if e.type == QUIT:
			running = False
		elif e.type == KEYDOWN:
			if e.key in MOVES.keys():
				moving = (moving[0] + MOVES[e.key][0], moving[1] + MOVES[e.key][1])	
		elif e.type == KEYUP:
			if e.key in MOVES.keys():
				moving = (moving[0] - MOVES[e.key][0], moving[1] - MOVES[e.key][1])
		elif e.type == GOTO:
			goto(e.x, e.y)

while running:
	clock.tick(7)
	handle()
	move(moving)
	for y in range(HEIGHT):
		for x in range(WIDTH):
			i,j = (slide_x+x,slide_y+y)
			screen.blit(tile[tilemap[j][i]], (x*TILE, y*TILE))
	for y in range(-6,HEIGHT):
		for x in range(-4,WIDTH):
			i, j = (x+slide_x,slide_y+y)
			if objmap[j][i] < 24:
				screen.blit(obj[objmap[j][i]], (x*TILE, y*TILE))
	pygame.display.flip()
