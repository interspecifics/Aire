#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRE v0.3, 2020+
----------------
> Now with ML!

conda create --name aire python=3.6
conda activate aire
pip install pygame
pip install oscpy
pip install scikit-learn

http://www.aire.cdmx.gob.mx/privado/WRI-Interspecific/

"""



import pygame
import json
import statistics, math
import pickle
import numpy as np
from sklearn.cluster import KMeans
from oscpy.client import OSCClient

pygame.init()
DATA_PATH = './db_aire.json'
MODEL_PATH = './models_aire.ml'
FONT_PATH = './RevMiniPixel.ttf'
N_CHANNELS = 9
N_ESTACIONES = 28

OSC_HOST = "127.0.0.1"
OSC_PORT = 8000
OSC_CLIENT = []
tempo = 1000

W = 700
H = 900

CO_1 = (255, 0, 0)
CO_2 = (0, 255, 0)
CO_3 = (0, 0, 255)
CO_L = (255, 255, 255)
CO_FR = (205,0,205)


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
        self.pos = []           #position
        self.sz = []            #size
        self.color = (0,255,0)  #color
        self.samples_o = []     #data, o3, no2, pm25
        self.samples_n = []
        self.samples_p = []
        self.a_o = 00           #actual o
        self.a_n = 00           #actual n
        self.a_p = 00           #actual p
        self.n = 96             #buffer size (4 days)
        self.esta = "[-]"
        # init pos and data
        self.pos = [x,y]
        self.samples_o = [0.0 for a in range(self.n)]
        self.samples_n = [0.0 for a in range(self.n)]
        self.samples_p = [0.0 for a in range(self.n)]
        self.font = pygame.font.Font(FONT_PATH, 14)
        self.freeze = False

        return

    def update(self, new_samples, nam, frz = False):
        # queue new sample and dequeue other data
        self.a_o = new_samples[0]
        self.a_n = new_samples[1]
        self.a_p = new_samples[2]
        self.samples_o.append(self.a_o)
        self.samples_n.append(self.a_n)
        self.samples_p.append(self.a_p)
        old_o = self.samples_o.pop(0)
        old_n = self.samples_n.pop(0)
        old_p = self.samples_p.pop(0)
        self.esta = nam
        self.freeze = frz
        return

    def draw(self, surf, dx, dy):
        # draw the list or create a polygon
        wi = 96*2
        he = 70
        max_o, max_n, max_p = max(self.samples_o), max(self.samples_n), max(self.samples_p)
        min_o, min_n, min_p = min(self.samples_o), min(self.samples_n), min(self.samples_p)
        # scale the points
        points_o = [[dx+i*2, dy+pmap(s, min_o, max_o, he, 0)] for i,s in enumerate(self.samples_o)]
        points_n = [[dx+i*2, dy+pmap(s, min_n, max_n, he, 0)] for i,s in enumerate(self.samples_n)]
        points_p = [[dx+i*2, dy+pmap(s, min_p, max_p, he, 0)] for i,s in enumerate(self.samples_p)]
        last_sample_o = self.samples_o[-1]
        last_sample_n = self.samples_n[-1]
        last_sample_p = self.samples_p[-1]
        actual_point_o = points_o[-1]
        actual_point_n = points_n[-1]
        actual_point_p = points_p[-1]
        # set on position
        points_o = [[dx,dy]] + points_o + [[dx+(len(self.samples_o)-1)*2, dy]]
        points_n = [[dx,dy]] + points_n + [[dx+(len(self.samples_n)-1)*2, dy]]
        points_p = [[dx,dy]] + points_p + [[dx+(len(self.samples_p)-1)*2, dy]]
        # draw the polygons
        pygame.draw.polygon(surf, CO_1, points_o, 1)
        pygame.draw.polygon(surf, CO_2, points_n, 1)
        pygame.draw.polygon(surf, CO_3, points_p, 1)
        # draw a double frame
        pygame.draw.rect(surf, G2, pygame.Rect(dx,dy,wi,he), 1)
        pygame.draw.rect(surf, G2, pygame.Rect(dx+wi-1,dy,184,he), 1)
        # actual-point lines
        pygame.draw.line(surf, CO_1, (actual_point_o[0]-3,actual_point_o[1]),(actual_point_o[0]+1,actual_point_o[1]), 2)
        pygame.draw.line(surf, CO_2, (actual_point_n[0]-3,actual_point_n[1]),(actual_point_n[0]+1,actual_point_n[1]), 2)
        pygame.draw.line(surf, CO_3, (actual_point_p[0]-3,actual_point_p[1]),(actual_point_p[0]+1,actual_point_p[1]), 2)
        # moving indicators
        pygame.draw.line(surf, G2, (dx+wi+58, dy),(dx+wi+58, dy+he), 1)
        pygame.draw.line(surf, G2, (dx+wi+62, dy),(dx+wi+62, dy+he), 1)
        pygame.draw.line(surf, CO_1, (actual_point_o[0]+60, actual_point_o[1]),(actual_point_o[0]+64, actual_point_o[1]), 2)
        pygame.draw.line(surf, G2, (dx+wi+118, dy),(dx+wi+118, dy+he), 1)
        pygame.draw.line(surf, G2, (dx+wi+122, dy),(dx+wi+122, dy+he), 1)
        pygame.draw.line(surf, CO_2, (actual_point_n[0]+120, actual_point_n[1]),(actual_point_n[0]+124, actual_point_n[1]), 2)
        pygame.draw.line(surf, G2, (dx+wi+178, dy),(dx+wi+178, dy+he), 1)
        pygame.draw.line(surf, G2, (dx+wi+182, dy),(dx+wi+182, dy+he), 1)
        pygame.draw.line(surf, CO_3, (actual_point_p[0]+180, actual_point_p[1]),(actual_point_p[0]+184, actual_point_p[1]), 2)
        # calculate a color
        le_color_mean = pygame.Color(int(pmap(last_sample_o, min_o, max_o, 0, 255)),
                                    int(pmap(last_sample_n, min_n, max_n, 255,0)),
                                    int(pmap(last_sample_p, min_p, max_p, 255,120)))
        # the labels n values
        l_o = self.font.render('  O3', 1, CO_1)
        l_n = self.font.render(' NO2', 1, CO_2)
        l_p = self.font.render('PM25', 1, CO_3)
        v_o = self.font.render('{:0.2f}'.format(last_sample_o), 1, CO_1)
        v_n = self.font.render('{:0.2f}'.format(last_sample_n), 1, CO_2)
        v_p = self.font.render('{:0.2f}'.format(last_sample_p), 1, CO_3)
        surf.blit(l_o, (315, dy+25))
        surf.blit(l_n, (375, dy+25))
        surf.blit(l_p, (435, dy+25))
        surf.blit(v_o, (315, dy+45))
        surf.blit(v_n, (375, dy+45))
        surf.blit(v_p, (435, dy+45))
        # draw another frame
        pygame.draw.rect(surf, G2, pygame.Rect(dx+wi+273, dy ,70, he), 1)#+30freeze+70ml
        n_estacion = self.font.render('# {} #'.format(self.esta), 1, CYAN)
        surf.blit(n_estacion, (dx+wi+280, dy+25)) # <- pos of <ESTACION>
        # freeze panel
        pygame.draw.rect(surf, G2, pygame.Rect(dx+wi+178, dy ,25, he), 1)#+30freeze
        if (self.freeze):
            pygame.draw.rect(surf, ORANGE, pygame.Rect(dx+wi+185, dy+2 ,15, he-4), 1)#+30freeze
        else:
            pygame.draw.rect(surf, G2, pygame.Rect(dx+wi+185, dy+2 ,15, he-4), 1)#+30freeze


        # ML panel
        pygame.draw.rect(surf, G2, pygame.Rect(dx+wi+203, dy ,70, he), 1)#+30freeze+70ml
        center_ml = [dx+wi+203+35, dy+he/2-5]
        r = he/2
        n_axis = 3
        rvs = [pmap(last_sample_o, min_o, max_o, 0, r),
                pmap(last_sample_n, min_n, max_n, 0, r),
                pmap(last_sample_p, min_p, max_p, 0, r)]
        points = []
        axises = []
        for a in range(n_axis):
            point = [center_ml[0] + rvs[a] * math.sin(a * (2*math.pi/n_axis)),
                    center_ml[1] + rvs[a] * math.cos(a * (2*math.pi/n_axis))]
            points.append(point)
            axis = [center_ml[0] + r * math.sin(a * (2*math.pi/n_axis)),
                    center_ml[1] + r * math.cos(a * (2*math.pi/n_axis))]
            axises.append(axis)
            pygame.draw.line(surf, G2, center_ml, axis, 1)
            pygame.draw.line(surf, GREEN, center_ml, point, 1)
        pygame.draw.polygon(surf, G2, axises, 1)
        pygame.draw.polygon(surf, GREEN, points, 1) # insert new color here
        return
# ... .... ... ... ... ... ... ... ... ... ... ... ... ... ... ... ... ... ...





# init
WINDOW = pygame.display.set_mode((W, H))

GREEN = (0, 255, 0)
G0 = (202, 220, 159)
G1 = (155, 188, 115)
G2 = (49, 98, 49)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0,0,0)
ORANGE = (255,127,0)
CYAN = (0, 255, 192)
BACKGROUND_COLOR = (0,0,63)

# load stuff, like fonts
FONT = pygame.font.Font(FONT_PATH, 16)
FONTmini = pygame.font.Font(FONT_PATH, 14)

# main screen for drawing buttons
DRAW_SCREEN = pygame.Surface((W,H))
#DRAW_SCREEN.fill((0,0,0,50))
PLOT_SCREEN = pygame.Surface((W,H))

# buttons
CHANNELS = ['0a','0b','0c','0d','0e','0f','0g','0h','0i']
LABELS = [FONT.render(cs, 1, (0, 255, 0)) for cs in CHANNELS]
# /BTN/ channel switch
BTNS_SWS = [pygame.draw.rect(DRAW_SCREEN, CYAN, pygame.Rect(50, 75+c*90, 60, 70), 1) for c in range(N_CHANNELS)]
#BTNS_MODES = [pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(100, 300+c*75, 50, 50), 1) for c in range(N_CHANNELS)]
# /BTN/ channel modes
BTNS_M1 = [pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(298, 75+c*90, 62, 70), 1) for c in range(N_CHANNELS)]
BTNS_M2 = [pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(298+62, 75+c*90, 62, 70), 1) for c in range(N_CHANNELS)]
BTNS_M3 = [pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(298+124, 75+c*90, 62, 70), 1) for c in range(N_CHANNELS)]
# /BTN/ station selector left
BTNS_STATS_L = [pygame.draw.rect(DRAW_SCREEN, BLUE, pygame.Rect(573, 75+c*90, 35, 70), 1) for c in range(N_CHANNELS)]
# /BTN/ station selector right
BTNS_STATS_R = [pygame.draw.rect(DRAW_SCREEN, (0,0,200), pygame.Rect(610, 75+c*90, 35, 70), 1) for c in range(N_CHANNELS)]
# /BTN/ station freeze
BTNS_FREEZE = [pygame.draw.rect(DRAW_SCREEN, (0,200,200), pygame.Rect(483, 75+c*90, 22, 70), 1) for c in range(N_CHANNELS)]
# /BTN/ channel date and time
BTN_DT = pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(390, 25, 100, 20), 1)
#pygame.draw.rect(surf, G2, pygame.Rect(dx+wi-1,dy,184,he), 1)

# timer events
TIC_EVENT = pygame.USEREVENT + 1
TIC_TIMER = tempo

#states and counters
clock = pygame.time.Clock()

sw_dt = True
sws = [False for c in range(N_CHANNELS)]
a_stats = [c  for c in range(N_CHANNELS)]       # actual stations for each channel
modes = [int(c/3)+1 for c in range(N_CHANNELS)] # mode 0 is off, 1 is o, 2 is n, 3 is p

freezes = [False, False, False, False, False, False, False, False, False]
actual_set = [0,0,0,0,0,0,0,0,0,""]
past_set = [0,0,0,0,0,0,0,0,0,""]
actual_labels = [0,0,0,0,0,0,0,0,0]
past_labels  =  [0,0,0,0,0,0,0,0,0]

a_contams  = [0,0,0,0,0,0,0,0]

pos = (0,0)
running = True
ii=0
index_estacion = 2
esta = "[*]"

db = {}
ee = [] #estaciones
ff = [] #fechas

PLOTS = [Plot(100, 200+i*90) for i in range(N_CHANNELS)]

# /-OSC-/
def init_osc(osc_host = OSC_HOST, osc_port = OSC_PORT):
    global OSC_CLIENT
    OSC_CLIENT = OSCClient(osc_host, osc_port)
    return

def update_data_send(i=0):
    global actual_set, actual_labels, past_labels
    print ('\t\t[timetag]: ', ff[i])
    # default values for sets
    #actual_set = [0,0,0,0,0,0,0,0,0,ff[i]]
    ##actual_labels = [0,0,0,0,0,0,0,0,0]
    #past_labels = [0,0,0,0,0,0,0,0,0]
    #a_label = 0
    # loop over each channel ch
    for j,ch in enumerate(CHANNELS):
        # when on, read data for station e in date ff[i]
        if (modes[j] != 0):
            e = ee[a_stats[j]]
            try:
                a_contams = db[e][ff[i]]
                a_label = models[a_stats[j]].labels_[i] #### #get current label
            except:
                print ("[---]: <<")
            if (not freezes[j]):
                a_v = a_contams[modes[j]-1]
                past_set[j] = actual_set[j]
                actual_set[j] = a_v
                past_labels[j] = actual_labels[j]
                actual_labels[j] = a_label
                ruta = '/aire/{}'.format(ch.lower())
                ruta = ruta.encode()
                OSC_CLIENT.send_message(ruta, [a_v])
                print("[_{}]: \t{:0.3f}\t({})\t[{}]".format(ch, a_v, e, a_label))
                # state tracking for labels osc a_label
                if (actual_labels[j] != past_labels[j]):
                    #past_labels[j] = actual_labels[j]
                    ruta = '/aire/{}/F{}'.format(ch.lower(), past_labels[j])
                    ruta = ruta.encode()
                    OSC_CLIENT.send_message(ruta, [0])
                    ruta = '/aire/{}/F{}'.format(ch.lower(), actual_labels[j])
                    ruta = ruta.encode()
                    OSC_CLIENT.send_message(ruta, [1])
            else:
                ruta = '/aire/{}'.format(ch.lower())
                ruta = ruta.encode()
                OSC_CLIENT.send_message(ruta, [past_set[j]])
                print("[_{}]: \t{:0.3f}\t({})\t[{}]".format(ch, past_set[j], e, a_label))
            # #####
        else:
            e = ee[a_stats[j]]
            a_contams = db[e][ff[i]]
            a_v = 0
            actual_set[j] = a_v
        # append data to plot
        #if (not freezes[j]):
        PLOTS[j].update(a_contams, e, freezes[j])
    # send date and time when sw_dt
    if (sw_dt):
        # date and time
        ttg = ff[ii].split()
        nu_r = '/aire/date'
        nu_r = nu_r.encode()
        OSC_CLIENT.send_message(nu_r, [ttg[0].encode()])
        #print(nu_r, ttg[0])
        nu_r = '/aire/time'
        nu_r = nu_r.encode()
        OSC_CLIENT.send_message(nu_r, [ttg[1].encode()])
        #print(nu_r, ttg[1])
    return


# -----------------------  -----------------------
def load_data_csv(fn='EXTRACT_20201125.06.csv'):
    """create an initial database from csv file"""
    global db, ee, ff
    ls = [l.strip() for l in open(fn, 'r+').readlines()]
    #create dictionary db[estacion][fecha]=[contams]
    db = {}
    act_contams = {}
    past_sta = ''
    sta = ''
    for i,l in enumerate(ls[1:]):
        ttg, sta, o3, no2, pm25 = l.split(',')
        if (sta != past_sta):
            #añade el dict pasado y crea nuevo
            if (past_sta != ''):
                db[past_sta] = act_contams
                act_contams = {}
            past_sta = sta
            print ('[csv]: \t' + past_sta)
        act_contams[ttg] = [float(o3), float(no2), float(pm25)]
        if (i==len(ls)-2):
            db[sta] = act_contams
            print ('[csv]: \t' + sta)
    # end loop
    ee = list(db.keys())
    ff = list(db[ee[0]].keys())
    print ('[csv]: '+ fn)
    return #db, ee, ff

def update_data_csv(fn='EXTRACT_20201127.06.csv'):
    """ update global db with new data"""
    global db, ee, ff
    ls = [l.strip() for l in open(fn, 'r+').readlines()]
    #añade fechas y contaminantes al registro de cada estación db[estacion][fecha]=[contams]
    for i,l in enumerate(ls[1:]):
        ttg, sta, o3, no2, pm25 = l.split(',')
        db[sta][ttg] = [float(o3), float(no2), float(pm25)]
    # end loop
    ee = list(db.keys())
    ff = list(db[ee[0]].keys())
    print ('[csv]: '+ fn)
    return #db, ee, ff

def dump_data():
    global db, ee, ff
    pack = db,ee,ff
    json.dump(pack, open(DATA_PATH,'r+'))
    print ("[DATA]: dumped: ", DATA_PATH)
    return

# -----------------------  -----------------------
onTrain = False
coloros = ['#1159FF', '#00FF38', '#FFEA12', '#FF7AA0', '#FF2812']
n_clusts = 5
datapoints = []
models = []
centers = []
clusters = []
actual_cluster = 0
actual_datapoint = np.zeros(3)
def train_models():
    global db, ee, ff, models
    for e in ee:
        datapoints = np.array([np.array([db[e][f][0], db[e][f][1], db[e][f][2]]) for f in ff])
        model = KMeans(init='k-means++', n_clusters=n_clusts, n_init=10)
        model.fit(datapoints)
        print ("[model]: fit ", e)
        models.append(model)
        #centers = model.cluster_centers_
        #clusters = model.labels_
    pickle.dump(models,open('models_aire.ml','wb'))
    print ("[model]: {} @ models.pck".format(len(ee)))
    return
# -----------------------  -----------------------


def load_data():
    global db,ee,ff
    # para acceder a los datos del archivo:
    pack = json.load(open(DATA_PATH,'r+'))
    db,ee,ff = pack
    print ("[DATA]: loaded")
    return

def load_models():
    global models
    models = pickle.load(open(MODEL_PATH, 'rb'))
    print ("[MODELS]: loaded")
    return

def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def tic():
    """ tic for the timer """
    global ii
    update_data_send(ii)
    if (ii<len(ff)-1):
        ii = ii+1
    else:
        ii=0
    #print ("\t\t -->   Aqui ENVIA DATOS")
    return

def handle_keys(event):
    """ handlear teclas ;D"""
    global running, stats
    """if (event.key == pygame.K_DOWN):
        running = False
    if (event.key == pygame.K_LEFT):
        if(stats[0]>0): stats[0]=stats[0]-1
    if (event.key == pygame.K_RIGHT):
        if(stats[0]<20): stats[0]=stats[0]+1"""

def exit_():
    """ to terminate"""
    global running
    running=False
    return

def handle_events():
    """ event handler with a dictionary"""
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
    global a_stats, modes, sw_dt, freezes
    # check for mouse pos and click
    pos = pygame.mouse.get_pos()
    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
    # clic on buttons (switches)
    for j,b in enumerate(BTNS_SWS):
        if (b.collidepoint(pos) and pressed1):
            modes[j] = 0
            #if (sws[j]==True):
            #    conts[j] = conts[j]+1
            print("[B{}]!: ".format(j), modes[j])
    # clic on buttons (modes)
    for j,b in enumerate(BTNS_M1):
        if (b.collidepoint(pos) and pressed1):
            modes[j] = 1
            print("[M{}]!: ".format(j), 1)
    for j,b in enumerate(BTNS_M2):
        if (b.collidepoint(pos) and pressed1):
            modes[j] = 2
            print("[M{}]!: ".format(j), 2)
    for j,b in enumerate(BTNS_M3):
        if (b.collidepoint(pos) and pressed1):
            modes[j] = 3
            print("[M{}]!: ".format(j), 3)
    # clic on buttons (conts_l)
    for j,b in enumerate(BTNS_STATS_L):
        if (b.collidepoint(pos) and pressed1):
            if (a_stats[j] > 0):
                a_stats[j] = a_stats[j] - 1
                print("[E{}]!: ".format(j), a_stats[j])
    # clic on buttons (conts_r)
    for j,b in enumerate(BTNS_STATS_R):
        if (b.collidepoint(pos) and pressed1):
            if (a_stats[j] < N_ESTACIONES):
                a_stats[j] = a_stats[j] + 1
                print("[E{}]!: ".format(j), a_stats[j])
    # clic on freeze btn
    for j,b in enumerate(BTNS_FREEZE):
        if (b.collidepoint(pos) and pressed1):
            freezes[j] = not freezes[j]
            print("[FREEZE] {}: {}".format(j, freezes[j]))
    # date and time button
    if (BTN_DT.collidepoint(pos) and pressed1):
        sw_dt = not sw_dt
        print("[DT{}]!: ".format(sw_dt))
    return


def update_graphics():
    global CO_1, CO_2, CO_3
    #updaye plots and other gui
    PLOT_SCREEN.fill((0,0,0,255))
    #plot_one.draw(PLOT_SCREEN, 100, 100)
    #BTNS_SWS = [pygame.draw.rect(PLOT_SCREEN, GREEN, pygame.Rect(100+c*75, 350, 50, 50), 2) for c in range(N_CHANNELS)]
    for c in range(N_CHANNELS):
        #
        if (modes[c]==1):
            CO_1 = GREEN
            CO_2 = G2
            CO_3 = G2
        elif(modes[c]==2):
            CO_1 = G2
            CO_2 = GREEN
            CO_3 = G2
        elif(modes[c]==3):
            CO_1 = G2
            CO_2 = G2
            CO_3 = GREEN
        else:
            CO_1 = G2
            CO_2 = G2
            CO_3 = G2
        # do plots           < .... POS HERE
        o_y = 60+c*90
        PLOTS[c].draw(PLOT_SCREEN, 110, o_y)
        # redo btns  <<<<<<      BTN HERE
        if(modes[c]>0): pygame.draw.rect(PLOT_SCREEN, G1, pygame.Rect(50, o_y, 60, 70), 1)
        else: pygame.draw.rect(PLOT_SCREEN, G1, pygame.Rect(50, o_y, 60, 70), 1)
    # blit on WINDOW
    WINDOW.blit(PLOT_SCREEN, (0, 0))
    # /SHOW/
    pygame.display.flip()
    return

def update_text():
    """update labels and other text in display"""
    global LABELS, actual_set, actual_set_means, CO_L
    # WINDOW.blit(DRAW_SCREEN, (0, 0))              <    ###  DEBUG HERE  ###
    # /LABELS/ upper
    AUX_LABEL = FONT.render('[ i n t e r s p e c i f i c s ]', 1, (64, 96, 0))
    WINDOW.blit(AUX_LABEL, (50, 870))
    AUX_LABEL = FONT.render(' [ AiRE ]', 1, GREEN)
    WINDOW.blit(AUX_LABEL, (50, 30))
    # /LABELS/ channels lab=name sta=value
    for j in range(N_CHANNELS):
        if (modes[j]>0):     LAB = FONT.render("[_"+CHANNELS[j]+"]", 1, GREEN)
        else:        LAB = FONT.render("[_"+CHANNELS[j]+"]", 1, G2)
        #WINDOW.blit(LABELS[j], (104+j*75, 354))
        if (modes[j]>0):     STA = FONTmini.render("{:0.2f}".format(actual_set[j]), 1, GREEN)
        else:        STA = FONTmini.render("{:0.2f}".format(actual_set[j]), 1, G2)
        CO_L = coloros[actual_labels[j]]
        aaa_lab = ''.join(["* " if actual_labels[j]==i  else '  ' for i in range(5)])
        if (modes[j]>0):
            BK = FONTmini.render("[           ]", 1, GREEN)
            MDL = FONTmini.render("  {} ".format(aaa_lab), 1, CO_L)
        else:
            BK = FONTmini.render("[           ]", 1, G2)
            MDL = FONTmini.render("  {} ".format(aaa_lab), 1, G2)
        WINDOW.blit(LAB, (60, 85 + j*90))
        WINDOW.blit(STA, (60, 105 + j*90))
        WINDOW.blit(MDL, (583, 105 + j*90))
        WINDOW.blit(BK, (583, 105 + j*90))
    # /LABELS/ bottom
    CUNT_LABEL = FONT.render("[step]:  {}".format(ii), 1, CYAN)
    WINDOW.blit(CUNT_LABEL, (550, 870))
    CUNT_LABEL = FONT.render("[timetag]:  "+ff[ii], 1, GREEN)
    WINDOW.blit(CUNT_LABEL, (400, 30))
    if (not sw_dt):
        CUNT_LABEL = FONT.render("[timetag]:  ", 1, G1)
        WINDOW.blit(CUNT_LABEL, (300, 870))
    # /SHOW/
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
    pygame.display.set_caption(' . A i R E . 2 0 2 0 + .')
    init_osc()
    load_data()
    if (onTrain):
        train_models()
    else:
        load_models()
    pygame.time.set_timer(TIC_EVENT, TIC_TIMER)
    game_loop()
    print("FIN DE LA TRANSMISSION //...")

if __name__=="__main__":
    main()










"""
#script for update data
------------------------
import json
db = {}
ee = [] #estaciones
ff = [] #fechas
DATA_PATH = "./db_aire.json"
load_data()
update_data_csv("EXTRACT_20201201.06.csv")
update_data_csv("EXTRACT_20201204.06.csv")
update_data_csv("EXTRACT_20201207.06.csv")
update_data_csv("EXTRACT_20201209.06.csv")
dump_data()
"""
