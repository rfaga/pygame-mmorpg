import pygame, cPickle
pygame.init()

tilemap = cPickle.load(file('data/tilemap.txt'))
objmap = cPickle.load(file('data/objmap.txt'))
running = True
screen = pygame.display.set_mode((640,480))
clock = pygame.time.Clock()

WIDTH, HEIGHT, TILE = 16, 11, 40

tile, obj = [], []

for i in range(24):
	tile += [pygame.image.load('imagens/tile%s.png'%i)]
	obj += [pygame.image.load('imagens/obj%s.png'%i)]

while running:
	clock.tick(7)
	for y in range(HEIGHT):
		for x in range(WIDTH):
			screen.blit(tile[tilemap[y][x]], (x*TILE, y*TILE))
	for y in range(-6, HEIGHT):
		for x in range(-4, WIDTH):
			if objmap[y][x] < 24:
				screen.blit(obj[objmap[y][x]], (x*TILE, y*TILE))	
	pygame.display.flip()
