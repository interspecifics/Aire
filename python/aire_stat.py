#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
AIRE 2020
--------------
Envia por OSC promedios de mediciones por contaminante (/aire/nox 126.12)
Usa datos históricos de enero a abril de 2020.

.Activa desactiva canales
.Elige modo por canal: estación o promedio
.Selecciona estación de cada canal
.plots!

1. cambia rutas de DATA_PATH y FONT_PATH
2. actualiza OSC_HOST y OSC_PORT
"""

import pygame
import json
import statistics
from oscpy.client import OSCClient


pygame.init()
DATA_PATH = "contaminantes_2020.JSON"
FONT_PATH = "RevMiniPixel.ttf"
N_CONTAMS = 9
N_ESTACIONES = 28

OSC_HOST = "127.0.0.1"
OSC_PORT = 8000
OSC_CLIENT = []

W = 850
H = 500


def pmap(value, inMin, inMax, outMin, outMax):
    """ like processing's map """
    inSpan = inMax - inMin
    outSpan = outMax - outMin
    try:
        transVal = float(value - inMin) / float(inSpan)
        return outMin + (transVal * outSpan)
    except:
        return 0


# ... .... ... ... ... ... ... ... ... ... ... ... ... ... ... ... ...
class Plot():
    def __init__(self, x, y):
        # create and update pixel-style plots
        self.pos = []       #position
        self.sz = []        #size
        self.color = (0,255,0)  #color
        self.samples = []   #data
        self.samples_mean = []
        self.a = 00         #actual sample
        self.b = 00         #actual mean
        self.n = 96         #number of samples
        self.esta = "[-]"
        # init pos and data
        self.pos = [x,y]
        self.samples = [0.0 for a in range(self.n)]
        self.samples_mean = [0.0 for a in range(self.n)]
        self.font = pygame.font.Font(FONT_PATH, 14)

        return

    def update(self, new_sample, new_mean, nam):
        # queue new sample and dequeue other data
        self.a = new_sample
        self.samples.append(self.a)
        old = self.samples.pop(0)
        self.b = new_mean
        self.samples_mean.append(self.b)
        old_mean = self.samples_mean.pop(0)
        self.esta = nam
        return

    def draw(self, surf, dx, dy):
        # draw the list or create a polygon
        wi = 50
        he = 96*2
        val_max = max(self.samples)
        val_min = min(self.samples)
        mean_max = max(self.samples_mean)
        mean_min = min(self.samples_mean)
        points = [[dx+pmap(s, val_min, val_max, 0, wi), dy+i*2] for i,s in enumerate(self.samples)]
        points_mean = [[dx+pmap(s, mean_min, mean_max, 0, wi), dy+i*2] for i,s in enumerate(self.samples_mean)]
        last_sample = self.samples[-1]
        last_sample_mean = self.samples_mean[-1]
        actual_point = points[-1]
        actual_point_mean = points_mean[-1]
        points = [[dx,dy]] + points + [[dx,dy+(len(self.samples)-1)*2]]
        points_mean = [[dx,dy]] + points_mean + [[dx,dy+(len(self.samples)-1)*2]]
        pygame.draw.polygon(surf, (0,64,0), points_mean, 1)
        pygame.draw.polygon(surf, GREEN, points, 1)
        pygame.draw.rect(surf, (0,64,0), pygame.Rect(dx,dy,wi,he), 1)
        pygame.draw.line(surf, GREEN, (actual_point[0],actual_point[1]-2),(actual_point[0],actual_point[1]+2), 2)
        pygame.draw.line(surf, (0,64,0), (actual_point_mean[0],actual_point_mean[1]-2),(actual_point_mean[0],actual_point_mean[1]+2), 2)

        pygame.draw.line(surf, (0,127,0), (dx,dy+he+29),(dx+50,dy+he+29), 1)
        pygame.draw.line(surf, (0,255,0), (actual_point[0],actual_point[1]+25),(actual_point[0],actual_point[1]+29), 2)
        pygame.draw.line(surf, (0,64,0), (actual_point_mean[0],actual_point_mean[1]+33),(actual_point_mean[0],actual_point_mean[1]+36), 2)
        le_color_mean = pygame.Color(int(pmap(last_sample_mean, mean_min, mean_max, 0, 255)),
                                    int(pmap(last_sample_mean, mean_min, mean_max, 255,0)),
                                    int(pmap(last_sample_mean, mean_min, mean_max, 255,120)))
        val = self.font.render('W: {:0.2f}'.format(last_sample), 1, GREEN)
        val_mean = self.font.render('M: {:0.2f}'.format(last_sample_mean), 1, (0,127,0))
        surf.blit(val, (dx, 98*2+105))
        surf.blit(val_mean, (dx, 98*2+134))
        n_estacion = self.font.render('< {} >'.format(self.esta), 1, GREEN)
        surf.blit(n_estacion, (dx, dy-20))
        return
# ... .... ... ... ... ... ... ... ... ... ... ... ... ... ... ... ...




estaciones = [
    {"sig":"AJM", "nombre":"Ajusco Medio", "id":"242"},
    {"sig":"ATI", "nombre":"Atizapán", "id":"243"},
    {"sig":"BJU", "nombre":"Benito Juárez", "id":"300"},
    {"sig":"CAM", "nombre":"Camarones", "id":"244"},
    {"sig":"CCA", "nombre":"Centro de Ciencias de la Atmósfera", "id":"245"},
    {"sig":"CHO", "nombre":"Chalco", "id":"246"},
    {"sig":"CUA", "nombre":"Cuajimalpa", "id":"248"},
    {"sig":"CUT", "nombre":"Cuautitlán", "id":"249"},
    {"sig":"FAC", "nombre":"FES Acatlán", "id":"250"},
    {"sig":"FAR", "nombre":"FES Aragón", "id":"431"},
    {"sig":"GAM", "nombre":"Gustavo A. Madero", "id":"302"},
    {"sig":"HGM", "nombre":"Hospital General de México", "id":"251"},
    {"sig":"IZT", "nombre":"Iztacalco", "id":"252"},
    {"sig":"LPR", "nombre":"La Presa", "id":"253"},
    {"sig":"LLA", "nombre":"Los Laureles", "id":"254"},
    {"sig":"MER", "nombre":"Merced", "id":"256"},
    {"sig":"MGH", "nombre":"Miguel Hidalgo", "id":"263"},
    {"sig":"NEZ", "nombre":"Nezahuacóyotl", "id":"258"},
    {"sig":"PED", "nombre":"Pedregal", "id":"259"},
    {"sig":"SAG", "nombre":"San Agustín", "id":"260"},
    {"sig":"SFE", "nombre":"Santa Fé", "id":"262"},
    {"sig":"SAC", "nombre":"Santiago Acahualtepec", "id":"432"},
    {"sig":"TAH", "nombre":"Tlahuac", "id":"265"},
    {"sig":"TLA", "nombre":"Tlalnepantla", "id":"266"},
    {"sig":"TLI", "nombre":"Tultitlán", "id":"267"},
    {"sig":"UIZ", "nombre":"UAM Iztapalapa", "id":"268"},
    {"sig":"UAX", "nombre":"UAM Xochimilco", "id":"269"},
    {"sig":"VIF", "nombre":"Villa de las Flores", "id":"270"},
    {"sig":"XAL", "nombre":"Xalostoc", "id":"271"}
    ]



# init
WINDOW = pygame.display.set_mode((W, H))

GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0,0,0)
ORANGE = (255,1,120)
BACKGROUND_COLOR = (0,0,63)

# load stuff, like fonts
FONT = pygame.font.Font(FONT_PATH, 16)
FONTmini = pygame.font.Font(FONT_PATH, 14)

# main screen for drawing buttons
DRAW_SCREEN = pygame.Surface((W,H))
DRAW_SCREEN.fill(BACKGROUND_COLOR)
PLOT_SCREEN = pygame.Surface((W,H))

# buttons
CONTAMS = ['CO','NO','NO2','NOX','O3','PM10','SO2','PM2','PMCO']
LABELS = [FONT.render(cs, 1, (0, 255, 0)) for cs in CONTAMS]
BTNS_SWS = [pygame.draw.rect(PLOT_SCREEN, GREEN, pygame.Rect(100+c*75, 350, 50, 50), 2) for c in range(N_CONTAMS)]
BTNS_MODES = [pygame.draw.rect(PLOT_SCREEN, RED, pygame.Rect(100+c*75, 300, 50, 50), 1) for c in range(N_CONTAMS)]
BTNS_STATS_L = [pygame.draw.rect(PLOT_SCREEN, BLUE, pygame.Rect(100+c*75, 50, 25, 50), 1) for c in range(N_CONTAMS)]
BTNS_STATS_R = [pygame.draw.rect(PLOT_SCREEN, BLUE, pygame.Rect(100+c*75+25, 50, 25, 50), 1) for c in range(N_CONTAMS)]


# timer events
TIC_EVENT = pygame.USEREVENT + 1
TIC_TIMER = 1000

#states and counters
clock = pygame.time.Clock()

sws = [False for c in range(N_CONTAMS)]
stats = [c  for c in range(N_CONTAMS)]
modes = [1 if (c < 5) else 0 for c in range(N_CONTAMS)] # mode 0 is mean, 1 is station

actual_set = [0,0,0,0,0,0,0,0,0,""]
actual_set_means = [0,0,0,0,0,0,0,0,0,""]
buffers = []
pos = (0,0)
running = True
ii=0
index_estacion = 2
esta = "[*]"

contaminantes = {}
fechas = []
current_means = []

PLOTS = [Plot(100+i*75, 200) for i in range(N_CONTAMS)]


# -osc
def init_osc(osc_host = OSC_HOST, osc_port = OSC_PORT):
    global OSC_CLIENT
    OSC_CLIENT = OSCClient(osc_host, osc_port)
    return
def update_data_send(i=0):
    global contaminantes, fechas, OSC_CLIENT, actual_set, actual_set_means
    print("\n\n[timetag]: ", fechas[i])
    pack = contaminantes['pollutionMeasurements']['date'][fechas[i]]
    substances = list(pack.keys())
    actual_set = [0,0,0,0,0,0,0,0,0,fechas[i]]
    actual_set_means = [0,0,0,0,0,0,0,0,0,fechas[i]]
    # -send
    for j,s in enumerate(substances):
        estado_estaciones = pack[s]
        lista_mediciones = [float(estado_estaciones[e]) for e in estado_estaciones.keys() if isFloat(estado_estaciones[e])]
        if (s == "PM2.5"): s = "PM2"
        # get the mean
        try:
            aux_mean = statistics.mean(lista_mediciones)
            actual_set_means[j] = aux_mean
        except:
            aux_mean = 0
            actual_set_means[j] = 0
        # get the simple data
        e=""
        esta="---"
        try:
            e = estaciones[stats[j]]["sig"]
            if (modes[j]): esta = e
            #print (estado_estaciones[e])
            if isFloat(estado_estaciones[e]):
                aux_sam = float(estado_estaciones[e])
            else:
                aux_sam = 0
            actual_set[j] = aux_sam
        except:
            aux_sam = 0
            actual_set[j] = aux_sam

        # send
        if sws[j]:
            ruta = '/aire/{}'.format(s.lower())
            ruta = ruta.encode()
            if (modes[j]):
                OSC_CLIENT.send_message(ruta, [aux_sam])
                print("{} \t{:0.3f}\t({})".format(s, aux_sam, e))
            else:
                OSC_CLIENT.send_message(ruta, [aux_mean])
                print("{} \t{:0.3f}\t({:d})".format(s, aux_mean, len(lista_mediciones)))
        # append data to set
        PLOTS[j].update(aux_sam, aux_mean, esta)
        #if (j==0): plot_one.update(aux_sam, aux_mean, esta)
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
    global running, stats
    """if (event.key == pygame.K_DOWN):
        running = False
    if (event.key == pygame.K_LEFT):
        if(stats[0]>0): stats[0]=stats[0]-1
    if (event.key == pygame.K_RIGHT):
        if(stats[0]<20): stats[0]=stats[0]+1"""

def exit_():
    global running
    running=False
    return

# handlear eventos con un diccionario
def handle_events():
    event_dict = {
        pygame.QUIT: exit_,
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
    global sws, stats, modes
    # check for mouse pos and click
    pos = pygame.mouse.get_pos()
    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
    # Check collision between buttons (switches) and mouse1
    for j,b in enumerate(BTNS_SWS):
        if (b.collidepoint(pos) and pressed1):
            sws[j] = not (sws[j])
            #if (sws[j]==True):
            #    conts[j] = conts[j]+1
            print("[B{}]!: ".format(j), sws[j])
    # Check collision between buttons (modes) and mouse1
    for j,b in enumerate(BTNS_MODES):
        if (b.collidepoint(pos) and pressed1):
            modes[j] = int(not modes[j])
            print("[M{}]!: ".format(j), modes[j])
    # Check collision between buttons (conts_l) and mouse1
    for j,b in enumerate(BTNS_STATS_L):
        if (b.collidepoint(pos) and pressed1):
            if (stats[j] > 0):
                stats[j] = stats[j] - 1
                print("[E{}]!: ".format(j), stats[j])
    # Check collision between buttons (conts_l) and mouse1
    for j,b in enumerate(BTNS_STATS_R):
        if (b.collidepoint(pos) and pressed1):
            if (stats[j] < N_ESTACIONES):
                stats[j] = stats[j] + 1
                print("[E{}]!: ".format(j), stats[j])
    return


def update_graphics():
    #updaye plots and other gui
    PLOT_SCREEN.fill((0,0,0,255))
    #plot_one.draw(PLOT_SCREEN, 100, 100)
    #BTNS_SWS = [pygame.draw.rect(PLOT_SCREEN, GREEN, pygame.Rect(100+c*75, 350, 50, 50), 2) for c in range(N_CONTAMS)]
    for c in range(N_CONTAMS):
        # do plots
        o_x = 100+c*75
        PLOTS[c].draw(PLOT_SCREEN, o_x, 100)
        # redo btns
        if(sws[c]): pygame.draw.rect(PLOT_SCREEN, GREEN, pygame.Rect(o_x, 350, 50, 50), 2)
        else: pygame.draw.rect(PLOT_SCREEN, (16,127,8), pygame.Rect(o_x, 350, 50, 50), 2)
    # blit on WINDOW
    WINDOW.blit(PLOT_SCREEN, (0, 0))
    pygame.display.flip()
    return

# update labels and other text in display
def update_text():
    global LABELS, actual_set, actual_set_means
    # blit on WINDOW
    #WINDOW.blit(DRAW_SCREEN, (0, 0))
    AUX_LABEL = FONT.render('-> i n t e r s p e c i f i c s : ', 1, (32, 48, 0))
    WINDOW.blit(AUX_LABEL, (100, 30))
    AUX_LABEL = FONT.render(' [ AIRE ]', 1, GREEN)
    WINDOW.blit(AUX_LABEL, (390, 30))
    for j in range(N_CONTAMS):
        if sws[j]:     LAB = FONT.render(CONTAMS[j], 1, (0, 255, 0))
        else:        LAB = FONT.render(CONTAMS[j], 1, (32, 24, 0))
        #WINDOW.blit(LABELS[j], (104+j*75, 354))
        if modes[j]:     STA = FONTmini.render("{:0.2f}".format(actual_set[j]), 1, (0, 255, 0))
        else:        STA = FONTmini.render("{:0.2f}".format(actual_set_means[j]), 1, (0,127,0))
        WINDOW.blit(LAB, (104+j*75, 354))
        WINDOW.blit(STA, (104+j*75, 384))
        # sign >
        SIG_LABEL = FONTmini.render(">", 1, (192,255,0))
        WINDOW.blit(SIG_LABEL, (92+j*75, 330-modes[j]*30))
    CUNT_LABEL = FONT.render("[step]:  {}".format(ii), 1, (16,64,32))
    WINDOW.blit(CUNT_LABEL, (450, 450))
    CUNT_LABEL = FONT.render("[timetag]:  "+actual_set_means[-1], 1, (16,64,32))
    WINDOW.blit(CUNT_LABEL, (100, 450))
    CUNT_LABEL = FONT.render("STAT:MMXX:", 1, (32,48,0))
    WINDOW.blit(CUNT_LABEL, (650, 450))
    pygame.display.flip()
    return




# the loop from outside
def game_loop():
    while running:
        handle_events()
        handle_mouse_clicks()
        update_graphics()
        update_text()
        clock.tick(9)

# the main (init+loop)
def main():
    pygame.display.set_caption(' . A i R E .')
    init_osc()
    load_data()
    pygame.time.set_timer(TIC_EVENT, TIC_TIMER)
    game_loop()
    print("FIN DE LA TRANSMISSION //...")

if __name__=="__main__":
    main()
