#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRE v:ML+w, 2020.12 [aire_mlw.py]
{--}-------------{--}
> Now with ML!
> And wordlwide cities

conda create --name aire python=3.6
conda activate aire
pip install pygame
pip install oscpy
pip install scikit-learn

http://www.aire.cdmx.gob.mx/privado/WRI-Interspecific/


>> 2021.C [aire_w+.py]
---------
support for new api
new stations list
>> 2021.01.21
-------------
double osc
lighter
-> tunear timerrs
-> osc: cont_index


>> 2021.01.23
requires buster w/python3.7
sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran
get last versions for scipy and scikit-learn from pywheels.org/simple/scipy
install with python3.7 -m pip install scipy0.19.0[...].whl


>> 2021.01.26 [aire_V3.py]
rpi 800x480
fullscreen



"""



import pygame
import json
import statistics, math, random
import pickle
import numpy as np
from sklearn.cluster import KMeans
from oscpy.client import OSCClient
from time import sleep

pygame.init()

DATA_PATH = './db_aire.json'
MODEL_PATH = './models_aire.ml'
DATA_PATH_CITIES = './db_aire_cities.json'
MODEL_PATH_CITIES = './models_aire_cities.ml'
N_ESTACIONES = 28
N_ESTACIONES_CITIES = 49

N_CHANNELS = 9
FONT_PATH = './RevMiniPixel.ttf'

OSC_HOST1 = "192.168.100.38"
OSC_PORT1 = 8000
OSC_HOST2 = "192.168.1.216"
OSC_PORT2 = 8888


OSC_CLIENT1 = []
tempo = 1000

W = 480
H = 800

CO_1 = (255, 0, 0)
CO_2 = (0, 255, 0)
CO_3 = (0, 0, 255)
CO_L = (255, 255, 255)
CO_FR = (205,0,205)


keys_cts = {
    'Rio_PedraDeGuaratiba':'RPGA',
    'Quito_Belisario':'QBEL',
    'WRI_Bogota_Centro_de_Alto_Rendimiento_CDAR': 'CDAR',
    'DoS_Bogota':'BOG',
    'DoS_JakartaCentral': 'DJKC',
    'Rio_Copacabana':'RCCB',
    'Quito_El_Camal':'QECA',
    'WRI_Bogota_Guaymaral_GYR': 'BOGY',
    'Rio_Tijuca':'RTIJ',
    'DoS_JakartaSouth':'DJKS',
    'Quito_Carapungo':'QCAR',
    'WRI_Bogota_Las_Ferias_LFR':'BOLF',
    'Rio_Centro':'RCEN',
    'DoS_Lima':'DLIM',
    'WRI_Bogota_MinAmbiente_MAM':'BOMA',
    'Quito_Centro':'QCEN',
    'Rio_SaoCristovao':'RSCR',
    'DoS_Shanghai':'DSHG',
    'WRI_Bogota_Puente_Aranda_PTE':'BOPA',
    'Quito_Cotocollao':'QCTC',
    'Rio_Bangu':'RBAG',
    'Quito_Guamani':'QGUA',
    'WRI_Bogota_Tunal_TUN':'BOTN',
    'Rio_CampoGrande':'RCGR',
    'Quito_Tumbaco':'QTUM',
    'WRI_Bogota_Usaquan_USQ':'BOUS',
    'Rio_Iraja':'RIRA',
    'Quito_LosChillos':'QLCH',
    'WRI_Guadalajara_Oblatos_OBL':'GDLO',
    'WRI_Monterrey_Cadereyta_MXMTYSE3':'MTYC',
    'WRI_Monterrey_La_Pastora_MXMTYSE1':'MTYP',
    'WRI_Monterrey_Obispado_MXMTYCE':'MTYO',
    'WRI_Sao_Paulo_Cerqueira_Cesar_CER':'SPCC',
    'WRI_Sao_Paulo_Cid_Universitaria__USP__IPEN_CUU':'SPCU',
    'WRI_Sao_Paulo_Congonhas_CON':'SPCO',
    'WRI_Sao_Paulo_Grajau__Parelheiros_GRA':'SPGP',
    'WRI_Sao_Paulo_Ibirapuera_IBI':'SPIB',
    'WRI_Sao_Paulo_Interlagos_INT':'SPIN',
    'WRI_Sao_Paulo_Itaim_Paulista_ITA':'SPIT',
    'WRI_Sao_Paulo_Marg_Tiete__Ponte_dos_Remedios_MAR':'SPMT',
    'WRI_Sao_Paulo_Mooca_MOO':'SPMO',
    'WRI_Sao_Paulo_Osasco_OSA':'SPOS',
    'WRI_Sao_Paulo_Parque_D_Pedro_II_PAR':'SPPP',
    'WRI_Sao_Paulo_Pico_do_Jaragua_PIC':'SPPJ',
    'WRI_Sao_Paulo_Pinheiros_PIN':'SPPI',
    'WRI_Sao_Paulo_Santana_SAN':'SPSA',
    'WRI_Leon_T21_T21':'LEON',
    'WRI_Salamanca_Nativitas_NAT':'NAT',
    'WRI_Bogota_Kennedy_KEN':'BOKE',
    'WRI_Bogota_Carvajal__Sevillana_CSE':'BOCS'}

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
        self.font = pygame.font.Font(FONT_PATH, 16)
        self.font2 = pygame.font.Font(FONT_PATH, 12)
        self.freeze = False
        self.cast = False

        return

    def update(self, new_samples, nam, frz = False, cst=False):
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
        self.cast=cst
        return

    def draw(self, surf, dx, dy):
        # draw the list or create a polygon
        wi = 96
        he = 70
        max_o, max_n, max_p = max(self.samples_o), max(self.samples_n), max(self.samples_p)
        min_o, min_n, min_p = min(self.samples_o), min(self.samples_n), min(self.samples_p)
        # scale the points
        points_o = [[dx+i, dy+pmap(s, min_o, max_o, he, 0)] for i,s in enumerate(self.samples_o)]
        points_n = [[dx+i, dy+pmap(s, min_n, max_n, he, 0)] for i,s in enumerate(self.samples_n)]
        points_p = [[dx+i, dy+pmap(s, min_p, max_p, he, 0)] for i,s in enumerate(self.samples_p)]
        last_sample_o = self.samples_o[-1]
        last_sample_n = self.samples_n[-1]
        last_sample_p = self.samples_p[-1]
        actual_point_o = points_o[-1]
        actual_point_n = points_n[-1]
        actual_point_p = points_p[-1]
        # set on position
        points_o = [[dx,dy]] + points_o + [[dx+(len(self.samples_o)-1), dy]]
        points_n = [[dx,dy]] + points_n + [[dx+(len(self.samples_n)-1), dy]]
        points_p = [[dx,dy]] + points_p + [[dx+(len(self.samples_p)-1), dy]]
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
        pygame.draw.line(surf, G2, (dx+wi+58, dy),(dx+wi+58, dy+he-1), 1)
        pygame.draw.line(surf, G2, (dx+wi+62, dy),(dx+wi+62, dy+he-1), 1)
        pygame.draw.line(surf, CO_1, (actual_point_o[0]+60, actual_point_o[1]),(actual_point_o[0]+64, actual_point_o[1]), 2)
        pygame.draw.line(surf, G2, (dx+wi+118, dy),(dx+wi+118, dy+he-1), 1)
        pygame.draw.line(surf, G2, (dx+wi+122, dy),(dx+wi+122, dy+he-1), 1)
        pygame.draw.line(surf, CO_2, (actual_point_n[0]+120, actual_point_n[1]),(actual_point_n[0]+124, actual_point_n[1]), 2)
        pygame.draw.line(surf, G2, (dx+wi+178, dy),(dx+wi+178, dy+he-1), 1)
        pygame.draw.line(surf, G2, (dx+wi+182, dy),(dx+wi+182, dy+he-1), 1)
        pygame.draw.line(surf, CO_3, (actual_point_p[0]+180, actual_point_p[1]),(actual_point_p[0]+184, actual_point_p[1]), 2)
        # calculate a color
        le_color_mean = pygame.Color(int(pmap(last_sample_o, min_o, max_o, 0, 255)),
                                    int(pmap(last_sample_n, min_n, max_n, 255,0)),
                                    int(pmap(last_sample_p, min_p, max_p, 255,120)))
        # the labels n values
        l_o = self.font2.render('  O3', 1, CO_1)
        l_n = self.font2.render(' NO2', 1, CO_2)
        l_p = self.font2.render('PM25', 1, CO_3)
        if (not self.cast):
            v_o = self.font.render('{:0.2f}'.format(last_sample_o), 1, CO_1)
            v_n = self.font.render('{:0.2f}'.format(last_sample_n), 1, CO_2)
            v_p = self.font.render('{:0.2f}'.format(last_sample_p), 1, CO_3)
        else:
            v_o = self.font.render('{:0.2f}'.format(last_sample_o/100), 1, CO_1)
            v_n = self.font.render('{:0.2f}'.format(last_sample_n/100), 1, CO_2)
            v_p = self.font.render('{:0.2f}'.format(last_sample_p/100), 1, CO_3)
        surf.blit(l_o, (350-170, dy+35))
        surf.blit(l_n, (405-170, dy+35))
        surf.blit(l_p, (460-170, dy+35))
        surf.blit(v_o, (330-170, dy+50))
        surf.blit(v_n, (390-170, dy+50))
        surf.blit(v_p, (450-170, dy+50))

        # draw another frame
        pygame.draw.rect(surf, G2, pygame.Rect(dx+wi+273, dy ,60, he), 1)#+30freeze+70ml
        n_estacion = self.font.render(':{}'.format(self.esta), 1, GREEN)
        if (big_mode==0):
            surf.blit(n_estacion, (dx+wi+297, dy+32)) # <- pos of <ESTACION>
        elif (big_mode==1):
            surf.blit(n_estacion, (dx+wi+288, dy+32)) # <- pos of <ESTACION>

        # freeze panel
        pygame.draw.rect(surf, G2, pygame.Rect(dx+wi+178, dy ,25, he), 1)#+30freeze
        if (self.freeze):
            pygame.draw.rect(surf, ORANGE, pygame.Rect(dx+wi+185, dy+2 ,15, he/2-2), 1)#+30freeze
        else:
            pygame.draw.rect(surf, G2, pygame.Rect(dx+wi+185, dy+2 ,15, he/2-2), 1)#+30freeze
        # cast
        if (self.cast==True):
            pygame.draw.rect(surf, CYAN, pygame.Rect(dx+wi+185, dy+2+he/2 ,15, he/2-4), 1)#+30freeze
        else:
            pygame.draw.rect(surf, G2, pygame.Rect(dx+wi+185, dy+2+he/2 ,15, he/2-4), 1)#+30freeze
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
FONTmini2 = pygame.font.Font(FONT_PATH, 12)

# main screen for drawing buttons
DRAW_SCREEN = pygame.Surface((W,H))
CITIES_SCREEN = pygame.Surface((W,H))
#DRAW_SCREEN.fill((0,0,0,50))
PLOT_SCREEN = pygame.Surface((W,H))

# buttons
CHANNELS = ['0A','0B','0C','0D','0E','0F','0G','0H','0I']
CHANNELS_CITIES = ['1A','1B','1C','1D','1E','1F','1G','1H','1I']

# /BTN/ channel switch
BTNS_SWS = [pygame.draw.rect(DRAW_SCREEN, CYAN, pygame.Rect(1, 30+c*80, 49, 70), 1) for c in range(N_CHANNELS)]
CTNS_SWS = [pygame.draw.rect(CITIES_SCREEN, CYAN, pygame.Rect(1, 30+c*80, 49, 70), 1) for c in range(N_CHANNELS)]
# /BTN/ channel modes
BTNS_M1 = [pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(142, 30+c*80, 62, 70), 1) for c in range(N_CHANNELS)]
BTNS_M2 = [pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(142+62, 30+c*80, 62, 70), 1) for c in range(N_CHANNELS)]
BTNS_M3 = [pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(142+124, 30+c*80, 62, 70), 1) for c in range(N_CHANNELS)]
CTNS_M1 = [pygame.draw.rect(CITIES_SCREEN, RED, pygame.Rect(142, 30+c*80, 62, 70), 1) for c in range(N_CHANNELS)]
CTNS_M2 = [pygame.draw.rect(CITIES_SCREEN, RED, pygame.Rect(142+62, 30+c*80, 62, 70), 1) for c in range(N_CHANNELS)]
CTNS_M3 = [pygame.draw.rect(CITIES_SCREEN, RED, pygame.Rect(142+124, 30+c*80, 62, 70), 1) for c in range(N_CHANNELS)]
# /BTN/ station selector left
BTNS_STATS_L = [pygame.draw.rect(DRAW_SCREEN, BLUE, pygame.Rect(573-156, 30+c*80, 35, 70), 1) for c in range(N_CHANNELS)]
CTNS_STATS_L = [pygame.draw.rect(CITIES_SCREEN, BLUE, pygame.Rect(573-156, 30+c*80, 35, 70), 1) for c in range(N_CHANNELS)]
# /BTN/ station selector right
BTNS_STATS_R = [pygame.draw.rect(DRAW_SCREEN, (0,0,200), pygame.Rect(608-156, 30+c*80, 35, 70), 1) for c in range(N_CHANNELS)]
CTNS_STATS_R = [pygame.draw.rect(CITIES_SCREEN, (0,0,200), pygame.Rect(608-156, 30+c*80, 35, 70), 1) for c in range(N_CHANNELS)]
# /BTN/ station freeze
BTNS_FREEZE = [pygame.draw.rect(DRAW_SCREEN, (0,200,200), pygame.Rect(483-156, 30+c*80, 22, 35), 1) for c in range(N_CHANNELS)]
CTNS_FREEZE = [pygame.draw.rect(CITIES_SCREEN, (0,200,200), pygame.Rect(483-156, 30+c*80, 22, 35), 1) for c in range(N_CHANNELS)]
# /BTN/ station freeze
BTNS_CAST = [pygame.draw.rect(DRAW_SCREEN, (200,200,0), pygame.Rect(483-156, 65+c*80, 22, 35), 1) for c in range(N_CHANNELS)]
CTNS_CAST = [pygame.draw.rect(CITIES_SCREEN, (200,200,0), pygame.Rect(483-156, 65+c*80, 22, 35), 1) for c in range(N_CHANNELS)]
# /BTN/ channel date and time
BTN_DT = pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(200, 5, 100, 20), 1)
CTN_DT = pygame.draw.rect(CITIES_SCREEN, RED, pygame.Rect(200, 5, 100, 20), 1)
# /BTN/ BIG MODE
BTN_BM = pygame.draw.rect(DRAW_SCREEN, CYAN, pygame.Rect(1, H-55, (W/2)-1, 30), 1)
CTN_BM = pygame.draw.rect(CITIES_SCREEN, CYAN, pygame.Rect(W/2, H-55, (W/2)-1, 30), 1)

# timer events
TIC_EVENT = pygame.USEREVENT + 1
TIC_TIMER = tempo

#states and counters
clock = pygame.time.Clock()

# switches, a_stats, modes
big_mode = 1
sw_dt = True
sws = [False for c in range(N_CHANNELS)]
a_stats = [c  for c in range(N_CHANNELS)]       # actual stations for each channel
modes = [int(c/3)+1 for c in range(N_CHANNELS)] # mode 0 is off, 1 is o, 2 is n, 3 is p
past_modes = [0 for c in range(N_CHANNELS)]
sw_dt_cts = True
sws_cts = [False for c in range(N_CHANNELS)]
a_stats_cts = [c  for c in range(N_CHANNELS)]       # actual stations for each channel
modes_cts = [int(c/3)+1 for c in range(N_CHANNELS)] # mode 0 is off, 1 is o, 2 is n, 3 is p
past_modes_cts = [0 for c in range(N_CHANNELS)]

# states
freezes = [False, False, False, False, False, False, False, False, False]
freezes_cts = [False, False, False, False, False, False, False, False, False]
casts = [False, False, False, False, False, False, False, False, False]
casts_cts = [False, False, False, False, False, False, False, False, False]
actual_set=[0,0,0,0,0,0,0,0,0]
actual_set_cts=[0,0,0,0,0,0,0,0,0]
past_set = [0,0,0,0,0,0,0,0,0]
past_set_cts = [0,0,0,0,0,0,0,0,0]
actual_labels = [0,0,0,0,0,0,0,0,0]
actual_labels_cts = [0,0,0,0,0,0,0,0,0]
past_labels = [0,0,0,0,0,0,0,0,0]
past_labels_cts = [0,0,0,0,0,0,0,0,0]
a_contams = [0,0,0,0,0,0,0,0,0]
a_contams_cts = [0,0,0,0,0,0,0,0,0]

pos = (0,0)
running = True
ii=0
jj=0
index_estacion = 2
index_estacion_cts = 2
esta = "[*]"
citi = "[*]"

db = {}
ee = [] #estaciones
ff = [] #fechas

db_cts = {}
ee_cts = [] #estaciones
ff_cts = [] #fechas


PLOTS = [Plot(100, 200+i*90) for i in range(N_CHANNELS)]
PLOTS_CTS = [Plot(100, 200+i*90) for i in range(N_CHANNELS)]

# /-OSC-/
def init_oscs(osc_host1 = OSC_HOST1,
            osc_port1 = OSC_PORT1,
            osc_host2 = OSC_HOST2,
            osc_port2 = OSC_PORT2
            ):
    global OSC_CLIENT1, OSC_CLIENT2
    OSC_CLIENT1 = OSCClient(osc_host1, osc_port1)
    OSC_CLIENT2 = OSCClient(osc_host2, osc_port2)
    return

def update_data_send(i=0):
    global actual_set, actual_labels, past_labels
    print ('\t\t[timetag]: ', ff[i])
    # loop over each channel ch
    for j,ch in enumerate(CHANNELS):
        # check for change in modes
        if (past_modes[j]!=modes[j]):
            # envia mensaje y actualiza past_modes[]
            ruta = '/aire/{}/m'.format(ch.upper())
            ruta = ruta.encode()
            OSC_CLIENT1.send_message(ruta, [modes[j]])
            OSC_CLIENT2.send_message(ruta, [modes[j]])
            past_modes[j] = modes[j]
        # when on, read data for station e in date ff[i]
        if (modes[j] != 0):
            e = ee[a_stats[j]]
            try:
                a_contams = db[e][ff[i]]
                a_label = models[a_stats[j]].labels_[i] #### #get current label
            except:
                print ("[---]: <<")
            if (not freezes[j]):
                if (casts[j]):
                    a_v = a_contams[modes[j]-1]/100
                else:
                    a_v = a_contams[modes[j]-1]
                past_set[j] = actual_set[j]
                actual_set[j] = a_v
                past_labels[j] = actual_labels[j]
                actual_labels[j] = a_label
                ruta = '/aire/{}'.format(ch.upper())
                ruta = ruta.encode()
                OSC_CLIENT1.send_message(ruta, [a_v])
                OSC_CLIENT2.send_message(ruta, [a_v])
                print("[_{}]: \t{:0.3f}\t({})\t[{}]".format(ch, a_v, e, a_label))
                # state tracking for labels osc a_label
                if (actual_labels[j] != past_labels[j]):
                    ruta = '/aire/{}/F{}'.format(ch.upper(), past_labels[j])
                    ruta = ruta.encode()
                    OSC_CLIENT1.send_message(ruta, [0])
                    OSC_CLIENT2.send_message(ruta, [0])
                    ruta = '/aire/{}/F{}'.format(ch.upper(), actual_labels[j])
                    ruta = ruta.encode()
                    OSC_CLIENT1.send_message(ruta, [1])
                    OSC_CLIENT2.send_message(ruta, [1])
            else:
                ruta = '/aire/{}'.format(ch.upper())
                ruta = ruta.encode()
                OSC_CLIENT1.send_message(ruta, [past_set[j]])
                OSC_CLIENT2.send_message(ruta, [past_set[j]])
                print("[_{}]: \t{:0.3f}\t({})\t[{}]".format(ch, past_set[j], e, a_label))
            # #####
        else:
            e = ee[a_stats[j]]
            a_contams = db[e][ff[i]]
            a_v = 0
            actual_set[j] = a_v
        # append data to plot
        PLOTS[j].update(a_contams, e, freezes[j], casts[j])
    # send date and time when sw_dt
    if (sw_dt):
        # date and time
        ttg = ff[ii].split()
        nu_r = '/aire/date'
        nu_r = nu_r.encode()
        OSC_CLIENT1.send_message(nu_r, [ttg[0].encode()])
        OSC_CLIENT2.send_message(nu_r, [ttg[0].encode()])
        #print(nu_r, ttg[0])
        nu_r = '/aire/time'
        nu_r = nu_r.encode()
        OSC_CLIENT1.send_message(nu_r, [ttg[1].encode()])
        OSC_CLIENT2.send_message(nu_r, [ttg[1].encode()])
        #print(nu_r, ttg[1])
    return

def update_data_send_cities(i=0):
    global actual_set_cts, actual_labels_cts, past_labels_cts
    print ('\t\t[timetag_world]: ', ff_cts[i])
    # loop over each channel ch
    for j,ch in enumerate(CHANNELS_CITIES):
        # check for change in modes
        if (past_modes_cts[j]!=modes_cts[j]):
            # envia mensaje y actualiza past_modes[]
            ruta = '/aire/{}/m'.format(ch.upper())
            ruta = ruta.encode()
            OSC_CLIENT1.send_message(ruta, [modes_cts[j]])
            OSC_CLIENT2.send_message(ruta, [modes_cts[j]])
            past_modes_cts[j] = modes_cts[j]
        # when on, read data for station e in date ff[i]
        if (modes_cts[j] != 0):
            e = ee_cts[a_stats_cts[j]]
            try:
                a_contams_cts = db_cts[e][ff_cts[i]]
                a_label_cts = models_cts[a_stats_cts[j]].labels_[i] #### #get current label
            except:
                print ("[---]: <<")
            if (not freezes_cts[j]):
                if (casts_cts[j]):
                    a_v = a_contams_cts[modes_cts[j]-1]/100
                else:
                    a_v = a_contams_cts[modes_cts[j]-1]
                past_set_cts[j] = actual_set_cts[j]
                actual_set_cts[j] = a_v
                past_labels_cts[j] = actual_labels_cts[j]
                actual_labels_cts[j] = a_label_cts
                ruta = '/aire/{}'.format(ch.upper())
                ruta = ruta.encode()
                OSC_CLIENT1.send_message(ruta, [a_v])
                OSC_CLIENT2.send_message(ruta, [a_v])
                print("[_{}]: \t{:0.3f}\t({})\t[{}]".format(ch, a_v, keys_cts[e], a_label_cts))
                # state tracking for labels osc a_label
                if (actual_labels_cts[j] != past_labels_cts[j]):
                    ruta = '/aire/{}/F{}'.format(ch.upper(), past_labels_cts[j])
                    ruta = ruta.encode()
                    OSC_CLIENT1.send_message(ruta, [0])
                    OSC_CLIENT2.send_message(ruta, [0])
                    ruta = '/aire/{}/F{}'.format(ch.upper(), actual_labels_cts[j])
                    ruta = ruta.encode()
                    OSC_CLIENT1.send_message(ruta, [1])
                    OSC_CLIENT2.send_message(ruta, [1])
            else:
                ruta = '/aire/{}'.format(ch.upper())
                ruta = ruta.encode()
                OSC_CLIENT1.send_message(ruta, [past_set_cts[j]])
                OSC_CLIENT2.send_message(ruta, [past_set_cts[j]])
                print("[_{}]: \t{:0.3f}\t({})\t[{}]".format(ch, past_set_cts[j], keys_cts[e], a_label_cts))
            # #####
        else:
            e = ee_cts[a_stats_cts[j]]
            a_contams_cts = db_cts[e][ff_cts[i]]
            a_v = 0
            actual_set_cts[j] = a_v
        # append data to plot
        PLOTS_CTS[j].update(a_contams_cts, keys_cts[e], freezes_cts[j], casts_cts[j])
    # send date and time when sw_dt
    if (sw_dt_cts):
        # date and time
        ttg = ff_cts[jj].split()
        nu_r = '/aire/w/date'
        nu_r = nu_r.encode()
        OSC_CLIENT1.send_message(nu_r, [ttg[0].encode()])
        OSC_CLIENT2.send_message(nu_r, [ttg[0].encode()])
        #print(nu_r, ttg[0])
        nu_r = '/aire/w/time'
        nu_r = nu_r.encode()
        OSC_CLIENT1.send_message(nu_r, [ttg[1].encode()])
        OSC_CLIENT2.send_message(nu_r, [ttg[1].encode()])
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
coloros = ['#1159FF', '#00FF38', '#FFEA12', '#FF7AA0', '#FF2812']
coloros = [(17,89,255),(0,255,56),(255,234,18),(255,122,160),(255,40,18)]

onTrain = False

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

n_clusts_cts = 5
models_cts = []
centers_cts = []
clusters_cts = []
actual_cluster_cts = 0
actual_datapoint_cts = np.zeros(3)
def train_models_cts():
    global db_cts, ee_cts, ff_cts, models_cts
    for e in ee_cts:
        try:
            datapoints = np.array([np.array([db_cts[e][f][0], db_cts[e][f][1], db_cts[e][f][2]]) for f in ff_cts])
            model = KMeans(init='k-means++', n_clusters=n_clusts_cts, n_init=10)
            model.fit(datapoints)
            print ("[model]: fit ", e)
            models_cts.append(model)
            #centers = model.cluster_centers_
            #clusters = model.labels_
        except:
            print ("[model]: wrong timetags ", e)
    pickle.dump(models_cts,open('models_aire_cities.ml','wb'))
    print ("[model]: {} @ models_aire_cts.ml".format(len(ee_cts)))
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

def load_data_cts():
    global db_cts, ee_cts, ff_cts
    # para acceder a los datos del archivo:
    pack = json.load(open(DATA_PATH_CITIES,'r+'))
    db_cts, ee_cts, ff_cts = pack
    print ("[DATA_CTS]: loaded")
    return
def load_models_cts():
    global models_cts
    models_cts = pickle.load(open(MODEL_PATH_CITIES, 'rb'))
    print ("[MODELS_CTS]: loaded")
    return


def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def tic():
    """ tic for the timer """
    global ii, jj
    update_data_send(ii)
    update_data_send_cities(jj)
    if (ii<len(ff)-1):
        ii = ii+1
    else:
        ii=0
    if (jj<len(ff_cts)-1):
        jj = jj+1
    else:
        jj=0
    #print ("\t\t -->   Aqui ENVIA DATOS")
    return

def handle_keys(event):
    """ handlear teclas ;D"""
    global running, stats
    if (event.key == pygame.K_q):
        running = False
    if (event.key==pygame.K_f):
        pygame.display.toggle_fullscreen()
        print("[FSXN]")
    sleep(0.02)
    """
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
    global a_stats, modes, sw_dt, freezes, a_stats_cts, modes_cts, sw_dt_cts, freezes_cts, big_mode
    # check for mouse pos and click
    pos = pygame.mouse.get_pos()
    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
    # first have to detect big_mode changes
    #
    # check everything if mode is 0: LOCAL
    if (big_mode==0):
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
        # clic on cast btn
        for j,b in enumerate(BTNS_CAST):
            if (b.collidepoint(pos) and pressed1):
                casts[j] = not casts[j]
                print("[CAST] {}: {}".format(j, casts[j]))
        # date and time button
        if (BTN_DT.collidepoint(pos) and pressed1):
            sw_dt = not sw_dt
            print("[DT{}]!: ".format(sw_dt))
        # big mode 0
        if (CTN_BM.collidepoint(pos) and pressed1):
            big_mode = 1
            print("[BIG_MODE]: {}".format(big_mode))
    # check everything if mode is 0: LOCAL
    elif (big_mode==1):
        # clic on buttons (switches)
        for j,b in enumerate(CTNS_SWS):
            if (b.collidepoint(pos) and pressed1):
                modes_cts[j] = 0
                #if (sws[j]==True):
                #    conts[j] = conts[j]+1
                print("[C{}]!: ".format(j), modes_cts[j])
        # clic on buttons (modes)
        for j,b in enumerate(CTNS_M1):
            if (b.collidepoint(pos) and pressed1):
                modes_cts[j] = 1
                print("[MC{}]!: ".format(j), 1)
        for j,b in enumerate(CTNS_M2):
            if (b.collidepoint(pos) and pressed1):
                modes_cts[j] = 2
                print("[MC{}]!: ".format(j), 2)
        for j,b in enumerate(CTNS_M3):
            if (b.collidepoint(pos) and pressed1):
                modes_cts[j] = 3
                print("[MC{}]!: ".format(j), 3)
        # clic on buttons (conts_l)
        for j,b in enumerate(CTNS_STATS_L):
            if (b.collidepoint(pos) and pressed1):
                if (a_stats_cts[j] > 0):
                    a_stats_cts[j] = a_stats_cts[j] - 1
                    print("[EC{}]!: ".format(j), a_stats_cts[j])
        # clic on buttons (conts_r)
        for j,b in enumerate(CTNS_STATS_R):
            if (b.collidepoint(pos) and pressed1):
                if (a_stats_cts[j] < N_ESTACIONES_CITIES):
                    a_stats_cts[j] = a_stats_cts[j] + 1
                    print("[EC{}]!: ".format(j), a_stats_cts[j])
        # clic on freeze btn
        for j,b in enumerate(CTNS_FREEZE):
            if (b.collidepoint(pos) and pressed1):
                freezes_cts[j] = not freezes_cts[j]
                print("[FREEZE_C] {}: {}".format(j, freezes_cts[j]))
        # clic on cast btn
        for j,b in enumerate(CTNS_CAST):
            if (b.collidepoint(pos) and pressed1):
                casts_cts[j] = not casts_cts[j]
                print("[CAST] {}: {}".format(j, casts_cts[j]))
        # date and time button
        if (CTN_DT.collidepoint(pos) and pressed1):
            sw_dt_cts = not sw_dt_cts
            print("[DTC{}]!: ".format(sw_dt_cts))
        # big mode 1
        if (BTN_BM.collidepoint(pos) and pressed1):
            big_mode = 0
            print("[BIG_MODE]: {}".format(big_mode))
    sleep(0.05)
    return


def update_graphics():
    global CO_1, CO_2, CO_3, big_mode
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
        # do plots         < .... POS HERE
        o_y = 30+c*80
        PLOTS[c].draw(PLOT_SCREEN, 50, o_y)
        # redo btns  <<<<<<      BTN HERE
        if(modes[c]>0):
            pygame.draw.rect(PLOT_SCREEN, GREEN, pygame.Rect(1, o_y, 49, 70), 1)
        else:
            pygame.draw.rect(PLOT_SCREEN, G2, pygame.Rect(1, o_y, 49, 70), 1)
    #big mode btts
    pygame.draw.rect(PLOT_SCREEN, GREEN, pygame.Rect(1, H-55, (W/2)-1, 30), 1)
    pygame.draw.rect(PLOT_SCREEN, G2, pygame.Rect(W/2, H-55, (W/2)-1, 30), 1)
    # blit on WINDOW
    WINDOW.blit(PLOT_SCREEN, (0, 0))
    # /SHOW/
    update_text()
    pygame.display.flip()
    return

def update_graphics_cts():
    global CO_1, CO_2, CO_3, big_mode
    #updaye plots and other gui
    PLOT_SCREEN.fill((0,0,0,255))
    #plot_one.draw(PLOT_SCREEN, 100, 100)
    #BTNS_SWS = [pygame.draw.rect(PLOT_SCREEN, GREEN, pygame.Rect(100+c*75, 350, 50, 50), 2) for c in range(N_CHANNELS)]
    for c in range(N_CHANNELS):
        #
        if (modes_cts[c]==1):
            CO_1 = GREEN
            CO_2 = G2
            CO_3 = G2
        elif(modes_cts[c]==2):
            CO_1 = G2
            CO_2 = GREEN
            CO_3 = G2
        elif(modes_cts[c]==3):
            CO_1 = G2
            CO_2 = G2
            CO_3 = GREEN
        else:
            CO_1 = G2
            CO_2 = G2
            CO_3 = G2
        # do plots           < .... POS HERE
        o_y = 30+c*80
        PLOTS_CTS[c].draw(PLOT_SCREEN, 50, o_y)
        # redo btns  <<<<<<      BTN HERE
        if(modes_cts[c]>0):
            pygame.draw.rect(PLOT_SCREEN, GREEN, pygame.Rect(1, o_y, 49, 70), 1)
        else:
            pygame.draw.rect(PLOT_SCREEN, G2, pygame.Rect(1, o_y, 49, 70), 1)
    pygame.draw.rect(PLOT_SCREEN, G2, pygame.Rect(1, H-55, (W/2)-1, 30), 1)
    pygame.draw.rect(PLOT_SCREEN, GREEN, pygame.Rect(W/2, H-55, (W/2)-1, 30), 1)

    # blit on WINDOW
    WINDOW.blit(PLOT_SCREEN, (0, 0))
    update_text_cts()
    # /SHOW/
    pygame.display.flip()
    return


def update_text():
    """update labels and other text in display"""
    global actual_set, CO_L
    #WINDOW.blit(DRAW_SCREEN, (0, 0))                  ###  < DEBUG HERE  ###
    # /LABELS/ upper
    AUX_LABEL = FONT.render('[ i n t e r s p e c i f i c s ]', 1, (64, 96, 0))
    WINDOW.blit(AUX_LABEL, (10, 782))
    AUX_LABEL = FONT.render(' [ AiRE ]', 1, GREEN)
    WINDOW.blit(AUX_LABEL, (10, 5))
    # /LABELS/ channels lab=name sta=value
    for j in range(N_CHANNELS):
        if (modes[j]>0):     LAB = FONT.render(":"+CHANNELS[j], 1, GREEN)
        else:        LAB = FONT.render(":"+CHANNELS[j], 1, G2)
        if (modes[j]>0):     STA = FONTmini2.render("{:0.2f}".format(actual_set[j]), 1, GREEN)
        else:        STA = FONTmini2.render("{:0.2f}".format(actual_set[j]), 1, G2)
        CO_L = coloros[actual_labels[j]]
        aaa_lab = ''.join(["*" if actual_labels[j]==i  else '  ' for i in range(5)])
        if (modes[j]>0):
            BK = FONTmini.render("[           ]", 1, GREEN)
            MDL = FONTmini.render("  {} ".format(aaa_lab), 1, CO_L)
        else:
            BK = FONTmini.render("[           ]", 1, G2)
            MDL = FONTmini.render("  {} ".format(aaa_lab), 1, G2)
        WINDOW.blit(LAB, (25, 62 + j*80))
        WINDOW.blit(STA, (15, 82 + j*80))
        WINDOW.blit(MDL, (592-170, 82 + j*80))
        WINDOW.blit(BK, (592-170, 82 + j*80))
    # /LABELS/ bottom
    CUNT_LABEL = FONT.render("[step]:  {}".format(ii), 1, CYAN)
    WINDOW.blit(CUNT_LABEL, (385, 782))
    CUNT_LABEL = FONT.render("[timetag]:  "+ff[ii], 1, GREEN)
    WINDOW.blit(CUNT_LABEL, (220, 5))
    if (not sw_dt):
        CUNT_LABEL = FONT.render("[timetag]:  ", 1, G1)
        WINDOW.blit(CUNT_LABEL, (220, 5))
    #
    BM_LABEL_a = FONT.render("MX", 1, GREEN)
    WINDOW.blit(BM_LABEL_a, (W/2 - 65, H-40))
    BM_LABEL_c = FONT.render("WW", 1, G2)
    WINDOW.blit(BM_LABEL_c, (W/2 + 45, H-40))
    # /SHOW/
    #pygame.display.flip()
    return


def update_text_cts():
    """update labels and other text in display"""
    global actual_set_cts, CO_L
    #WINDOW.blit(CITIES_SCREEN, (0, 0))                  ###  < DEBUG BTNS HERE  ###
    # /LABELS/ upper
    AUX_LABEL = FONT.render('[ i n t e r s p e c i f i c s ]', 1, (64, 96, 0))
    WINDOW.blit(AUX_LABEL, (10, 782))
    AUX_LABEL = FONT.render(' [ AiRE ]', 1, GREEN)
    WINDOW.blit(AUX_LABEL, (10, 5))
    # /LABELS/ channels lab=name sta=value
    for j in range(N_CHANNELS):
        if (modes_cts[j]>0):     LAB = FONT.render(":"+CHANNELS_CITIES[j], 1, GREEN)
        else:        LAB = FONT.render(":"+CHANNELS_CITIES[j], 1, G2)
        if (modes_cts[j]>0):     STA = FONTmini2.render("{:0.2f}".format(actual_set_cts[j]), 1, GREEN)
        else:        STA = FONTmini2.render("{:0.2f}".format(actual_set_cts[j]), 1, G2)
        CO_L = coloros[actual_labels_cts[j]]
        aaa_lab = ''.join(["*" if actual_labels_cts[j]==i  else '  ' for i in range(5)])
        if (modes_cts[j]>0):
            BK = FONTmini.render("[           ]", 1, GREEN)
            MDL = FONTmini.render("  {} ".format(aaa_lab), 1, CO_L)
        else:
            BK = FONTmini.render("[           ]", 1, G2)
            MDL = FONTmini.render("  {} ".format(aaa_lab), 1, G2)
        WINDOW.blit(LAB, (25, 62 + j*80))
        WINDOW.blit(STA, (15, 82 + j*80))
        WINDOW.blit(MDL, (592-170, 82 + j*80))
        WINDOW.blit(BK, (592-170, 82 + j*80))
    # /LABELS/ bottom
    CUNT_LABEL = FONT.render("[step]:  {}".format(jj), 1, CYAN)
    WINDOW.blit(CUNT_LABEL, (385, 782))
    CUNT_LABEL = FONT.render("[timetag]:  "+ff_cts[jj], 1, GREEN)
    WINDOW.blit(CUNT_LABEL, (220, 5))
    if (not sw_dt_cts):
        CUNT_LABEL = FONT.render("[timetag]:  ", 1, G1)
        WINDOW.blit(CUNT_LABEL, (220, 5))
    #
    BM_LABEL_a = FONT.render("MX", 1, G2)
    WINDOW.blit(BM_LABEL_a, (W/2 - 65, H-40))
    BM_LABEL_c = FONT.render("WW", 1, GREEN)
    WINDOW.blit(BM_LABEL_c, (W/2 + 45, H-40))


    # /SHOW/
    #pygame.display.flip()
    return



# the loop from outside
def game_loop():
    while running:
        handle_events()
        handle_mouse_clicks()
        if (big_mode==0):
            update_graphics()
            #update_text()
        elif(big_mode==1):
            update_graphics_cts()
            #update_text_cts()
        clock.tick(90)

# the main (init+loop)
def main():
    na = random.randint(1, 14)
    lia = ['~' for a in range(na)]
    stra = '~'.join(lia)
    pygame.display.set_caption('[ {} ]'.format(stra))
    init_oscs()
    load_data()
    load_data_cts()
    if (onTrain):
        train_models()
        train_models_cts()
    else:
        load_models()
        load_models_cts()
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
