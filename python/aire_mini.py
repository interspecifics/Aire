#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
AIRE 2020.mini
--------------
Envia por OSC promedios de mediciones por contaminante (/aire/nox 126.12)
Usa datos históricos de enero a abril de 2020.
Permite seleccionar canales activos.
"""

import pygame
import json
import statistics
from oscpy.client import OSCClient

# init
pygame.init()

DATA_PATH = 'D:/SK/py/aire/contaminantes_2020.JSON'
FONT_PATH = 'D:/SK/py/aire/RevMiniPixel.ttf'

OSC_HOST = "192.168.1.141"
OSC_PORT = 8000
OSC_CLIENT = []

WIDTH = 600
HEIGHT = 300
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0,0,0)
ORANGE = (232,111,97)
BACKGROUND_COLOR = BLACK

# load stuff, like fonts
FONT = pygame.font.Font(FONT_PATH, 16)
FONTmini = pygame.font.Font(FONT_PATH, 14)

# main screen for drawing buttons
DRAW_SCREEN = pygame.Surface((WIDTH,HEIGHT))
DRAW_SCREEN.fill(BACKGROUND_COLOR)

# buttons
CONTAMS = ['CO','NO','NO2','NOX','O3','PM10','SO2','PM2','PMCO']
BTNS = [pygame.draw.rect(DRAW_SCREEN, GREEN, pygame.Rect(100+c*50, 100, 50, 50), 2) for c in range(9)]
LABELS = [FONT.render(cs, 1, (0, 255, 0)) for cs in CONTAMS]

# timer events
TIC_EVENT = pygame.USEREVENT + 1
TIC_TIMER = 1000

#states and counters
clock = pygame.time.Clock()
actual_set = [0,0,0,0,0,0,0,0,0,""]
buffers = []
sws = [False for c in range(9)]
conts = [0  for c in range(9)]
pos = (0,0)
running = True
ii=0

contaminantes = {}
fechas = []
current_means = []


# -osc
def init_osc(osc_host = OSC_HOST, osc_port = OSC_PORT):
	global OSC_CLIENT
	OSC_CLIENT = OSCClient(osc_host, osc_port)
	return
def update_data_send(i=0):
	global contaminantes, fechas, OSC_CLIENT, actual_set
	print("\n\n[timetag]: ", fechas[i])
	pack = contaminantes['pollutionMeasurements']['date'][fechas[i]]
	substances = list(pack.keys())
	actual_set = [0,0,0,0,0,0,0,0,0,fechas[i]]
	# -send
	for j,s in enumerate(substances):
		estado_estaciones = pack[s]
		lista_mediciones = [float(estado_estaciones[e]) for e in estado_estaciones.keys() if isFloat(estado_estaciones[e])]
		if (s == "PM2.5"): s = "PM2"
		try:
			# send()
			aux_mean = statistics.mean(lista_mediciones)
			actual_set[j] = aux_mean
			ruta = '/aire/{}'.format(s.lower())	
			ruta = ruta.encode()
			if sws[j]:
				OSC_CLIENT.send_message(ruta, [aux_mean])
				print("{} \t{:0.3f}\t({:d})".format(s, aux_mean, len(lista_mediciones)))
		except:
			print("None")
	return

# -data stuff
def load_data():
	global contaminantes,fechas
	# para acceder a los datos del archivo:
	contaminantes = json.load(open(DATA_PATH,'r+')) 
	_dates = contaminantes['pollutionMeasurements']['date'].keys()
	fechas = list(_dates)
	print ("[DATA]: ok")
	return

def isFloat(s):
	try: 
		float(s)
		return True
	except ValueError:
		return False



# tic for the timer
def tic():
	global ii
	update_data_send(ii)
	ii = ii+1
	#print ("\t\t -->   Aqui ENVIA DATOS")
	return

# handlear teclas ;D;D
def handle_keys(event):
	global running
	if (event.key == pygame.K_DOWN):
		running = False

# handlear eventos con un diccionario
def handle_events():
	event_dict = {
		pygame.QUIT: exit,
		pygame.KEYDOWN: handle_keys,
		TIC_EVENT: tic
		}
	for event in pygame.event.get():
		if event.type in event_dict:
			if (event.type==pygame.KEYDOWN):
				event_dict[event.type](event)
			else:
				event_dict[event.type]()
	return

# handlear clicks del mouse
def handle_mouse_clicks():
	global sws, conts
	# check for mouse pos and click
	pos = pygame.mouse.get_pos()
	pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
	# Check collision between buttons and mouse1
	for j,b in enumerate(BTNS):
		if (b.collidepoint(pos) and pressed1):
			sws[j] = not (sws[j])
			if (sws[j]==True):
				conts[j] = conts[j]+1
			print("[B{}]!: ".format(j), conts[j])
	return


# update labels and other text in display
def update_text():
	global LABELS, actual_set
	WINDOW.blit(DRAW_SCREEN, (0, 0))
	AUX_LABEL = FONT.render('->i n t e r e s p e c i f i c s:  ', 1, (32, 48, 0))
	WINDOW.blit(AUX_LABEL, (100, 50))
	AUX_LABEL = FONT.render('[ AIRE ] -mini-', 1, GREEN)
	WINDOW.blit(AUX_LABEL, (320, 50))
	for j in range(9):
		WINDOW.blit(LABELS[j], (104+j*50, 104))
		if sws[j]:
			STA = FONTmini.render("{:0.2f}".format(actual_set[j]), 1, (0, 255, 0))
		else:
			STA = FONTmini.render("{:0.2f}".format(actual_set[j]), 1, (32,48, 0))
		WINDOW.blit(STA, (104+j*50, 134))
	CUNT_LABEL = FONTmini.render("[step]:  {}".format(ii), 1, ORANGE)
	WINDOW.blit(CUNT_LABEL, (100, 180))
	CUNT_LABEL = FONTmini.render("[timetag]:  "+actual_set[-1], 1, ORANGE)
	WINDOW.blit(CUNT_LABEL, (220, 180))
	CUNT_LABEL = FONTmini.render("mmxx", 1, (32,48,0))
	WINDOW.blit(CUNT_LABEL, (500, 180))
	pygame.display.flip()





# the loop from outside
def game_loop():
	while running:
		handle_events()
		handle_mouse_clicks()
		update_text()
		clock.tick(9)

# the main (init+loop)
def main():
	pygame.display.set_caption('[ i n t e r s p e c i f i c s : A I R E ]')
	init_osc()
	load_data()
	pygame.time.set_timer(TIC_EVENT, TIC_TIMER)
	game_loop()
	print("FIN DE LA TRANSMISSION //...")
	
if __name__=="__main__":
	main()










