# -*- coding: utf-8 -*-

"""
aire 1.0
---------
cada hora recupera datos de la medición de contaminantes
de las estaciones del sistema de monitoreo de calidad de aire de cdmx,
almacena un registro temporal y le procesa para enviarle como
mensajes OSC a intervalos regulares
"""

import requests, cPickle, OSC
from bs4 import BeautifulSoup as BS
from time import localtime, time, sleep, asctime

# --vars
send_period = 0.1
get_period = 3600
osc_host = "127.0.0.1"
osc_port = 57121


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


def send_current(ip, ik, iy, cOsc):
	current_param = params[ip]
	current_station = nk[current_param][ik]
	current_val = data_ring[current_param][iy][ik]

	#route = "/"+current_station+"/"+data_ring[current_param][iy][0]+"/"+data_ring[current_param][iy][1]+"/"+current_param
	route = "/"+current_station
	msg = OSC.OSCMessage()
	msg.setAddress(route)
	try:
		msg.append( float(current_val) )
	except:
		msg.append( current_val )
	cOsc.send(msg)
	return route+" "+current_val


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
		mms = send_current(ip, ik, iy, cOsc)
		ik += 1
		if( ik >= len(nk[params[ip]]) ):
			ik = 2
			ip += 1
			if (ip>=len(params)):
				ip = 0
				iy = iy-1
				if ( abs(iy) > len(data_ring[params[ip]]) ):
					iy = -1
		print "[> >] :: {",ik, ip, iy,"} :: "+mms
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
	# end while
