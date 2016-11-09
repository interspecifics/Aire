# -*- coding: utf-8 -*-

"""
aire 1.1
---------
cada hora recupera datos de la medición de contaminantes
de las estaciones del sistema de monitoreo de calidad de aire de cdmx,
almacena un registro temporal y le procesa para enviarle como
mensajes OSC a intervalos regulares

1.1 Envia los promedios por contaminante
"""

import requests, cPickle, OSC
from bs4 import BeautifulSoup as BS
from time import localtime, time, sleep, asctime

# --vars
send_period = 0.1
get_period = 3600
osc_host = "127.0.0.1"
<<<<<<< HEAD
osc_port = 57120
nsteps = 24
=======
osc_port = 57121
nsteps = 1
>>>>>>> origin/master


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
	for p in params:
		qparam = p
		url = "http://www.aire.df.gob.mx/estadisticas-consultas/concentraciones/respuesta.php?qtipo="+qtipo+"&parametro="+qparam+"&anio="+qanio+"&qmes="+qmes
		html = requests.get(url).text
		soup = BS(html, "html.parser")
		table = soup.find('table')
		table_rows = table.find_all('tr')

		register =table_rows[-1].find_all('td')
		new_reg = []
		for r in register:
			new_reg.append(r.text.rstrip().strip())
		new_data[p] = new_reg

		stats =table_rows[1].find_all('td')
		nkys = []
		for i in range(len(new_reg)):
			nkys.append( stats[i].text.rstrip().strip() )
		new_keys[p] = nkys
		print p,
	print " :: .OK"
	return new_data, new_keys


def send_current(ip, iy, cOsc):
	current_param = params[ip]
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
	cOsc.send(msg)
	return route+" "+str(current_mean)


if __name__ == "__main__":
	# -- inits
	params = ['so2', 'co', 'nox', 'no2', 'no', 'o3', 'pm10', 'pm2', 'wsp', 'wdr', 'tmp', 'rh']
	data_ring={}
	ip = 0
	iy = -1
	ik = 2
	send_addr = osc_host, osc_port
	cOsc = OSC.OSCClient()
	cOsc.connect(send_addr)
	# -- load past data
	try:
		data_ring = cPickle.load(open('aire_data.cpk', 'r'))
		nd, nk = update_stations();
		for p in params:
			data_ring[p].append(nd[p])
			if len(data_ring[p])>24:
				data_ring = data_ring[-25:]
		print "[._.]: aire_data loaded"
	except:
		data_ring = {}
		nd, nk = update_stations();
		for p in params:
			data_ring[p] = []
			data_ring[p].append(nd[p])
		cPickle.dump(data_ring, open("aire_data.cpk","w"))
		cPickle.dump(nk, open("aire_keys.cpk","w"))
		print "[·-·]: aire_data created"

	# -- the loop
	t0 = time()
	while ( True ):
		# -- stream data
		mms = send_current(ip, iy, cOsc)
		ip += 1
		if (ip>=len(params)):
			ip = 0
			iy = iy-1
			if ( abs(iy) > min([nsteps, len( data_ring[params[ip]] )]) ):
				iy = -1
		print "[ >>] :: {",ip, iy,"} :: "+mms
		# --update
		if ( abs(time()-t0) > get_period ):
			nd, nk = update_stations();
			for p in params:
				data_ring[p].append(nd[p])
				if len(data_ring[p])>24:
					data_ring = data_ring[-25:]
			cPickle.dump(data_ring, open("aire_data.cpk","w"))
			cPickle.dump(nk, open("aire_keys.cpk","w"))
			t0 = time()
			print "\n[* *] :: updated at ::" + asctime()
		else:
			# --sleep
			sleep(send_period)
	# end whilep
