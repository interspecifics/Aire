#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRE, 2020B


2020.11.26
----------

conda create --name aire python=3.6
conda activate aire
pip install pygame
pip install oscpy


"""



import pygame
import json
import statistics
from oscpy.client import OSCClient


pygame.init()
DATA_PATH = './db_aire.json'
FONT_PATH = './RevMiniPixel.ttf'
N_CHANNELS = 9
N_ESTACIONES = 28

OSC_HOST = "192.168.1.83"
OSC_PORT = 8000
OSC_CLIENT = []

W = 600
H = 900

CO_1 = (255, 0, 0)
CO_2 = (0, 255, 0)
CO_3 = (0, 0, 255)



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
        self.samples_o = []   #data, o3, no2, pm25
        self.samples_n = []
        self.samples_p = []
        self.a_o = 00         #actual o
        self.a_n = 00         #actual n
        self.a_p = 00         #actual p
        self.n = 96          #buffer size
        self.esta = "[-]"
        # init pos and data
        self.pos = [x,y]
        self.samples_o = [0.0 for a in range(self.n)]
        self.samples_n = [0.0 for a in range(self.n)]
        self.samples_p = [0.0 for a in range(self.n)]
        self.font = pygame.font.Font(FONT_PATH, 14)

        return

    def update(self, new_samples, nam): 
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
        return

    def draw(self, surf, dx, dy):
        # draw the list or create a polygon
        wi = 96*2
        he = 50
        max_o, max_n, max_p = max(self.samples_o), max(self.samples_n), max(self.samples_p)
        min_o, min_n, min_p = min(self.samples_o), min(self.samples_n), min(self.samples_p)
        points_o = [[dx+i*2, dy+pmap(s, min_o, max_o, he, 0)] for i,s in enumerate(self.samples_o)]
        points_n = [[dx+i*2, dy+pmap(s, min_n, max_n, he, 0)] for i,s in enumerate(self.samples_n)]
        points_p = [[dx+i*2, dy+pmap(s, min_p, max_p, he, 0)] for i,s in enumerate(self.samples_p)]
        last_so = self.samples_o[-1]
        last_sn = self.samples_n[-1]
        last_sp = self.samples_p[-1]
        actual_point_o = points_o[-1]
        actual_point_n = points_n[-1]
        actual_point_p = points_p[-1]
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
        # actual point lines
        pygame.draw.line(surf, CO_1, (actual_point_o[0]-3,actual_point_o[1]),(actual_point_o[0]+1,actual_point_o[1]), 2)
        pygame.draw.line(surf, CO_2, (actual_point_n[0]-3,actual_point_n[1]),(actual_point_n[0]+1,actual_point_n[1]), 2)
        pygame.draw.line(surf, CO_3, (actual_point_p[0]-3,actual_point_p[1]),(actual_point_p[0]+1,actual_point_p[1]), 2)
        # little moving indicators
        pygame.draw.line(surf, G2, (dx+wi+58, dy),(dx+wi+58, dy+50), 1)
        pygame.draw.line(surf, G2, (dx+wi+62, dy),(dx+wi+62, dy+50), 1)
        pygame.draw.line(surf, CO_1, (actual_point_o[0]+60, actual_point_o[1]),(actual_point_o[0]+64, actual_point_o[1]), 2)
        pygame.draw.line(surf, G2, (dx+wi+118, dy),(dx+wi+118, dy+50), 1)
        pygame.draw.line(surf, G2, (dx+wi+122, dy),(dx+wi+122, dy+50), 1)
        pygame.draw.line(surf, CO_2, (actual_point_n[0]+120, actual_point_n[1]),(actual_point_n[0]+124, actual_point_n[1]), 2)
        pygame.draw.line(surf, G2, (dx+wi+178, dy),(dx+wi+178, dy+50), 1)
        pygame.draw.line(surf, G2, (dx+wi+182, dy),(dx+wi+182, dy+50), 1)
        pygame.draw.line(surf, CO_3, (actual_point_p[0]+180, actual_point_p[1]),(actual_point_p[0]+184, actual_point_p[1]), 2)
        # calculate a color        
        le_color_mean = pygame.Color(int(pmap(last_so, min_o, max_o, 0, 255)),
                                    int(pmap(last_sn, min_n, max_n, 255,0)),
                                    int(pmap(last_sp, min_p, max_p, 255,120)))
        # the values
        l_o = self.font.render('  O3', 1, CO_1)
        l_n = self.font.render(' NO2', 1, CO_2)
        l_p = self.font.render('PM25', 1, CO_3)
        v_o = self.font.render('{:0.2f}'.format(last_so), 1, CO_1)
        v_n = self.font.render('{:0.2f}'.format(last_sn), 1, CO_2)
        v_p = self.font.render('{:0.2f}'.format(last_sp), 1, CO_3)
        surf.blit(l_o, (305, dy+10))
        surf.blit(l_n, (365, dy+10))
        surf.blit(l_p, (425, dy+10))
        surf.blit(v_o, (305, dy+30))
        surf.blit(v_n, (365, dy+30))
        surf.blit(v_p, (425, dy+30))
        # draw another frame
        pygame.draw.rect(surf, G2, pygame.Rect(dx+wi+183, dy ,70, he), 1)
        n_estacion = self.font.render('< {} >'.format(self.esta), 1, ORANGE)
        surf.blit(n_estacion, (dx+wi+195, dy+30)) # <- pos of <ESTACION>
        return
# ... .... ... ... ... ... ... ... ... ... ... ... ... ... ... ... ...




ee = [] #estaciones
ff = [] #fechas

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
BTNS_SWS = [pygame.draw.rect(DRAW_SCREEN, ORANGE, pygame.Rect(50, 75+c*90, 50, 50), 1) for c in range(N_CHANNELS)]
#BTNS_MODES = [pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(100, 300+c*75, 50, 50), 1) for c in range(N_CHANNELS)]
BTNS_M1 = [pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(292, 75+c*90, 64, 50), 1) for c in range(N_CHANNELS)]
BTNS_M2 = [pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(292+64, 75+c*90, 64, 50), 1) for c in range(N_CHANNELS)]
BTNS_M3 = [pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(292+128, 75+c*90, 64, 50), 1) for c in range(N_CHANNELS)]
BTN_DT = pygame.draw.rect(DRAW_SCREEN, RED, pygame.Rect(300, 870, 100, 20), 1)
#pygame.draw.rect(surf, G2, pygame.Rect(dx+wi-1,dy,184,he), 1)
BTNS_STATS_L = [pygame.draw.rect(DRAW_SCREEN, BLUE, pygame.Rect(485, 75+c*90, 30, 50), 1) for c in range(N_CHANNELS)]
BTNS_STATS_R = [pygame.draw.rect(DRAW_SCREEN, (0,0,200), pygame.Rect(510, 75+c*90, 30, 50), 1) for c in range(N_CHANNELS)]

sw_dt = True

# timer events
TIC_EVENT = pygame.USEREVENT + 1
TIC_TIMER = 500

#states and counters
clock = pygame.time.Clock()

sws = [False for c in range(N_CHANNELS)]        
a_stats = [c  for c in range(N_CHANNELS)]       # actual stations for each channel
modes = [int(c/3)+1 for c in range(N_CHANNELS)] # mode 0 is off, 1 is o, 2 is n, 3 is p

actual_set = [0,0,0,0,0,0,0,0,0,""]
actual_set_means = [0,0,0,0,0,0,0,0,0,""]
pos = (0,0)
running = True
ii=0
index_estacion = 2
esta = "[*]"

contaminantes = {}
fechas = []
current_means = []
 
PLOTS = [Plot(100, 200+i*90) for i in range(N_CHANNELS)]


# -osc
def init_osc(osc_host = OSC_HOST, osc_port = OSC_PORT):
    global OSC_CLIENT
    OSC_CLIENT = OSCClient(osc_host, osc_port)
    return

def update_data_send(i=0):
    global actual_set
    print ('\t\t[timetag]: ', ff[i])
    actual_set = [0,0,0,0,0,0,0,0,0,ff[i]]
    for j,ch in enumerate(CHANNELS):
        if (modes[j] != 0):
            e = ee[a_stats[j]]
            a_contams = db[e][ff[i]]
            a_v = a_contams[modes[j]-1]
            actual_set[j] = a_v
            ruta = '/aire/{}'.format(ch.lower())    
            ruta = ruta.encode()
            OSC_CLIENT.send_message(ruta, [a_v])
            print("[_{}]: \t{:0.3f}\t({})".format(ch, a_v, e))
        else:
            e = ee[a_stats[j]]
            a_contams = db[e][ff[i]]
            a_v = 0
            actual_set[j] = a_v
        # append data to plot
        PLOTS[j].update(a_contams, e)
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


# -data stuff
def load_data_csv(fn='EXTRACT_20201125.06.csv'):
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
            #añade el dict pasado
            if (past_sta != ''):
                db[past_sta] = act_contams
                #crea nuevo dict
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

def load_data():
    global db,ee,ff
    # para acceder a los datos del archivo:
    pack = json.load(open(DATA_PATH,'r+')) 
    db,ee,ff = pack
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
    if (ii<len(ff)-1):
        ii = ii+1
    else:
        ii=0
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
    global a_stats, modes, sw_dt
    # check for mouse pos and click
    pos = pygame.mouse.get_pos()
    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
    # Check collision between buttons (switches) and mouse1
    for j,b in enumerate(BTNS_SWS):
        if (b.collidepoint(pos) and pressed1):
            modes[j] = 0
            #if (sws[j]==True):
            #    conts[j] = conts[j]+1
            print("[B{}]!: ".format(j), modes[j])
    # Check collision between buttons (modes) and mouse1
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
    # Check collision between buttons (conts_l) and mouse1
    for j,b in enumerate(BTNS_STATS_L):
        if (b.collidepoint(pos) and pressed1):
            if (a_stats[j] > 0):
                a_stats[j] = a_stats[j] - 1
                print("[E{}]!: ".format(j), a_stats[j])
    # Check collision between buttons (conts_r) and mouse1
    for j,b in enumerate(BTNS_STATS_R):
        if (b.collidepoint(pos) and pressed1):
            if (a_stats[j] < N_ESTACIONES):
                a_stats[j] = a_stats[j] + 1
                print("[E{}]!: ".format(j), a_stats[j])
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
        o_y = 75+c*90
        PLOTS[c].draw(PLOT_SCREEN, 100, o_y)
        # redo btns
        if(modes[c]>0): pygame.draw.rect(PLOT_SCREEN, G1, pygame.Rect(50, o_y, 50, 50), 1)
        else: pygame.draw.rect(PLOT_SCREEN, G1, pygame.Rect(50, o_y, 50, 50), 1)
    # blit on WINDOW
    WINDOW.blit(PLOT_SCREEN, (0, 0))
    #WINDOW.blit(DRAW_SCREEN, (0, 0))
    pygame.display.flip()
    return

# update labels and other text in display
def update_text():
    global LABELS, actual_set, actual_set_means
    # blit on WINDOW
    #WINDOW.blit(DRAW_SCREEN, (0, 0))
    AUX_LABEL = FONT.render('-> i n t e r s p e c i f i c s ]', 1, (64, 96, 0))
    WINDOW.blit(AUX_LABEL, (350, 30))
    AUX_LABEL = FONT.render(' [ AIRE ]', 1, GREEN)
    WINDOW.blit(AUX_LABEL, (50, 30))
    for j in range(N_CHANNELS): 
        if (modes[j]>0):     LAB = FONT.render("[_"+CHANNELS[j]+"]", 1, GREEN)
        else:        LAB = FONT.render("[_"+CHANNELS[j]+"]", 1, G2)
        #WINDOW.blit(LABELS[j], (104+j*75, 354))
        if (modes[j]>0):     STA = FONTmini.render("{:0.2f}".format(actual_set[j]), 1, GREEN)
        else:        STA = FONTmini.render("{:0.2f}".format(actual_set_means[j]), 1, G2)
        WINDOW.blit(LAB, (55, 105 + j*90))
        WINDOW.blit(STA, (55, 85 + j*90))
        # sign >
        #SIG_LABEL = FONTmini.render(">", 1, (192,255,0))
        #WINDOW.blit(SIG_LABEL, (92+j*75, 330-modes[j]*30))
    CUNT_LABEL = FONT.render("[step]:  {}".format(ii), 1, ORANGE)
    WINDOW.blit(CUNT_LABEL, (50, 870))
    CUNT_LABEL = FONT.render("[timetag]:  "+ff[ii], 1, GREEN)
    WINDOW.blit(CUNT_LABEL, (300, 870))
    if (not sw_dt):
        CUNT_LABEL = FONT.render("[timetag]:  ", 1, G1)
        WINDOW.blit(CUNT_LABEL, (300, 870))
    #CUNT_LABEL = FONT.render("STAT:MMXX:", 1, (32,48,0))
    #WINDOW.blit(CUNT_LABEL, (650, 870))
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
    pygame.display.set_caption(' . A i R E . 2 0 b .')
    init_osc()
    load_data()
    pygame.time.set_timer(TIC_EVENT, TIC_TIMER)
    game_loop()
    print("FIN DE LA TRANSMISSION //...")
    
if __name__=="__main__":
    main()










