# -*- coding: utf-8 -*-

"""
interspecifics // aire 2.0.1
---------------------------
cada hora recupera datos de la medición de contaminantes
de las estaciones del sistema de monitoreo de calidad de aire de cdmx,
almacena un registro temporal y le procesa para enviarle como
mensajes OSC a intervalos regulares
adds dataring and timelapse functions, updates .cpk,
and streams timelapse data

1.1 usa los promedios por contaminante
2.0 streamea datos de las ultimas 24 horas cada hora
2.0.1 envia datos a dos clientes OSC
"""

import requests, cPickle, OSC
from bs4 import BeautifulSoup as BS
from time import localtime, time, sleep, asctime

# --vars
send_period = 0.1
send_period_2 = 0.05
get_period = 3600

#osc_host1 = "127.0.0.15"
osc_host1 = "192.168.1.66"
osc_port1 = 57120
osc_host2 = "192.168.1.67"
osc_port2 = 57120

def lerp(a, b, d):
	return a * (1 - d) + b * d

def update_stations_24():
	""" create queries, fetch data, parse & return data and keys"""
	contams = ['so2', 'co', 'nox', 'no2', 'no', 'o3', 'pm10', 'pm2', 'wsp', 'wdr', 'tmp', 'rh']
	new_data = {}
	new_keys = {}
	qanio = str(localtime().tm_year)
	qmes = str(localtime().tm_mon)
	qtipo = 'HORARIOS'

	print "[--------------------------------------------]"
	print "[••••••••••••••••••••••••••••••••••••••••••••]"
	print "[I N T E R S P E C I F I C S .]"
	print "[AIRE.2.0.1 - 2019]"
	print "[loading stations]"
	print "[data available] >> "
	print "[reading values:]",

	for p in contams:
		#--- make request, get table
		qcontam = p
		url = "http://www.aire.df.gob.mx/estadisticas-consultas/concentraciones/respuesta.php?qtipo="+qtipo+"&parametro="+qcontam+"&anio="+qanio+"&qmes="+qmes
		html = requests.get(url).text
		soup = BS(html, "html.parser")
		table = soup.find('table')
		table_rows = table.find_all('tr')
		#--- get size
		regis = table_rows[-1].find_all('td')
		last_reg = [r.text.rstrip().strip() for r in regis]
		sz_reg = len(last_reg)
		#--- get header
		head =table_rows[1].find_all('td')
		nkys = [k.text.rstrip().strip() for k in head[:sz_reg]]
		#--- get data
		new_data[p] = []
		regisss = table_rows[-24].find_all('td')
		for h in range(0,24):
			new_reg = [r.text.rstrip().strip() for r in regisss[sz_reg*h:sz_reg*(h+1)] ]
			new_data[p].append(new_reg)

		print "\t",p,
	print "\t[::]"
	return new_data, new_keys


def update_stations():
	""" create queries, fetch data, parse & return data and keys"""
	ip = 0
	iy = -1
	ik = 2
	new_data = {}
	new_keys = {}
	qanio = str(localtime().tm_year)
	qmes = str(localtime().tm_mon)
	qtipo = 'HORARIOS'
	print "[·_.] :: stations :: ",
	for p in contams:
		qparam = p
		url = "http://www.aire.df.gob.mx/estadisticas-consultas/concentraciones/respuesta.php?qtipo="+qtipo+"&parametro="+qparam+"&anio="+qanio+"&qmes="+qmes
		html = requests.get(url).text
		soup = BS(html, "html.parser")
		table = soup.find('table')
		table_rows = table.find_all('tr')
		#--- ..
		register =table_rows[-1].find_all('td')
		new_reg = []
		for r in register:
			new_reg.append(r.text.rstrip().strip())
		new_data[p] = new_reg
		#--- .
		stats =table_rows[1].find_all('td')
		nkys = []
		for i in range(len(new_reg)):
			nkys.append( stats[i].text.rstrip().strip() )
		new_keys[p] = nkys
		print p,
	print " :: .OK"
	return new_data, new_keys


def send_current(ip, iy, cOsc1, cOsc2):
	current_param = contams[ip]
	current_mean = 0.0;
	nv = 0;
	#print data_ring[current_param][iy]
	for val in data_ring[current_param][iy][2:]:
		if not val.isalpha():
			current_mean = current_mean + float(val)
			nv = nv + 1
	if nv != 0:
		current_mean = current_mean/float(nv)
	else:
		current_mean = 0

	route = "/"+current_param
	msg = OSC.OSCMessage()
	msg.setAddress(route)
	msg.append( current_mean )
	cOsc1.send(msg)
	cOsc2.send(msg)
	return route+"/"+str(current_mean)


def send_current_2(ii, ty, jj, cOsc1, cOsc2):
	#--- calculate for current
	actual_param = contams[jj]
	current_mean = 0.0;
	nv = 0;
	for val in data_ring[actual_param][-1][2:]:
		if not val.isalpha():
			current_mean = current_mean + float(val)
			nv = nv + 1
	if nv != 0:
		current_mean = current_mean/float(nv)
	else:
		current_mean = 0

	#--- calculate for past
	past_mean = 0.0;
	nv = 0;
	for val in data_ring[actual_param][-2][2:]:
		if not val.isalpha():
			past_mean = past_mean + float(val)
			nv = nv + 1
	if nv != 0:
		past_mean = past_mean/float(nv)
	else:
		past_mean = 0

	#--- interpolate with ty
	actual_val = lerp(past_mean, current_mean, ty)

	#--- make and send actual message
	route = "/"+actual_param
	msg = OSC.OSCMessage()
	msg.setAddress(route)
	msg.append( actual_val )
	cOsc1.send(msg)
	cOsc2.send(msg)
	return route+"/"+str(actual_val)



if __name__ == "__main__":
	#--- basic inits
	contams = ['so2', 'co', 'nox', 'no2', 'no', 'o3', 'pm10', 'pm2', 'wsp', 'wdr', 'tmp', 'rh']
	data_ring = {}
	nsteps = 24
	ip = 0
	iy = -1
	ik = 2
	send_addr1 = osc_host1, osc_port1
	send_addr2 = osc_host2, osc_port2
	cOsc1 = OSC.OSCClient()
	cOsc1.connect(send_addr1)
	cOsc2 = OSC.OSCClient()
	cOsc2.connect(send_addr2)
	cycle = 0
	ncy = 12			#set timelapse repetitions=time
	in_cycle=0
	in_ncy=96			#set stream interpolating points
	#--- download new data
	try:
		data_ring, nk = update_stations_24();
		print "[aire_data] :: updated"
		cPickle.dump(data_ring, open("aire_data.cpk","w"))
		cPickle.dump(nk, open("aire_keys.cpk","w"))
		print "[aire_data] :: data files created"
	#--- or load from file
	except:
		try:
			data_ring = cPickle.load(open('aire_data.cpk', 'r'))
			nk = cPickle.load(open('aire_keys.cpk', 'r'))
			print "[aire_data] :: loaded from filws"
		except:
			print "[aire_data] :: x.X"

	#--- start 24 stream
	print "\n\n[aire_data] :: data lapse [24] stream :: [**-*++-*.]"

	#--- --- the loop
	t0 = time()
	while ( True ):
		#--- stream data
		mms = send_current(ip, iy, cOsc1, cOsc2)
		#--- counter engine
		if ip==0:
			#for i in range(100): print "\b",
			ty = str(data_ring[contams[ip]][iy][0])+"-"+str(data_ring[contams[ip]][iy][1])
			print "\n["+ty+"]",
		ip += 1
		if (ip>=len(contams)):
			ip = 0
			iy = iy-1
			if ( abs(iy) > min([nsteps, len( data_ring[contams[ip]] )]) ):
				iy = -1
				cycle+=1
		#--- print
		print "  ",mms[:10],
		#--- time to interpolate
		if cycle>=ncy:
			print "\n\n[aire_data] :: start current data stream :: [...---***]"
			#- loop on current
			for ii in range(in_ncy):
				#--- string with percentage
				ty = ii/float(in_ncy)
				print "\n["+str(ii+1)+"/"+str(in_ncy)+"]",
				#--- send contaminants
				for jj,c in enumerate(contams):
					#--- send data
					mms = send_current_2(ii, ty, jj, cOsc1, cOsc2)
					print "  ",mms[:10],
					sleep(send_period)
			#- restart cy
			cycle=0
			print "\n\n[aire_data] :: data lapse [24] stream :: [**-*++-*.]"

		#--- time to update
		if ( abs(time()-t0) > get_period ):
			#--- get new data
			try:
				data_ring, nk = update_stations_24();
				print "[aire_data] :: updated"
				cPickle.dump(data_ring, open("aire_data.cpk","w"))
				cPickle.dump(nk, open("aire_keys.cpk","w"))
				print "[aire_data] :: data files created"
			#--- or keep historic
			except:
				print "[aire_data] ::  badupdate, keep historic data"
			#--- restart timer
			t0 = time()
			print "\n[aire_data] ::" + asctime()
		#--- sleep
		else:
			sleep(send_period_2)
	# end whilep
