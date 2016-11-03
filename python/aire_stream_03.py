# -*- coding: utf-8 -*-

"""
aire 0.1
---------
0. read old data
1. keep a buffer ciclically repeating
2. get new data periodically
	2.1 extract and parse
	2.2 add to ring buffer
	2.3 save new data
"""


# imports
import requests, cPickle, OSC
from bs4 import BeautifulSoup as BS
from time import localtime, time, sleep, asctime


# update stations
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
	print "[fetching]: ",
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
	print "-OK"
	return new_data, new_keys



# get the current indexes and send osc
def send_current(ip, ik, iy, cOsc):
	current_param = params[ip]
	current_station = nk[current_param][ik]
	current_val = data_ring[current_param][iy][ik]

	route = "/"+current_station+"/"+data_ring[current_param][iy][0]+"/"+data_ring[current_param][iy][1]+"/"+current_param
	msg = OSC.OSCMessage()
	msg.setAddress(route)
	try:
		msg.append( float(current_val) )
	except:
		msg.append( current_val )
	cOsc.send(msg)
	return



# main loop
if __name__ == "__main__":
	params = ['so2', 'co', 'nox', 'no2', 'no', 'o3', 'pm10', 'pm2', 'wsp', 'wdr', 'tmp', 'rh']
	data_ring={}
	ip = 0
	iy = -1
	ik = 2
	try:
		data_ring = cPickle.load(open('aire_data.cpk', 'r'))
		nd, nk = update_stations();
		for p in params:
			data_ring[p].append(nd[p])
			if len(data_ring[p])>24:
				data_ring = data_ring[-25:]
		print "[._·]: aire_data loaded"
	except:
		data_ring = {}
		nd, nk = update_stations();
		for p in params:
			data_ring[p] = []
			data_ring[p].append(nd[p])
		cPickle.dump(data_ring, open("aire_data.cpk","w"))
		cPickle.dump(nk, open("aire_keys.cpk","w"))
		print "[._.]: aire_data created"

	send_addr = "127.0.0.1", 8000
	cOsc = OSC.OSCClient()
	cOsc.connect(send_addr)
	#init_data_ring()
	t0 = time()
	while ( True ):
		#stream data
		send_current(ip, ik, iy, cOsc)
		ik += 1
		if( ik >= len(nk[params[ip]]) ): 
			ik = 2
			ip += 1
			if (ip>=len(params)):
				ip = 0
				iy = iy-1
				if ( abs(iy) > len(data_ring[params[ip]]) ):
					iy = -1
		print "[indexes]:",ik, ip, iy
		#update
		if ( abs(time()-t0) > 600 ):
			# update data_buffer
			nd, nk = update_stations();
			for p in params:
				data_ring[p].append(nd[p])
				if len(data_ring[p])>24:
					data_ring = data_ring[-25:]
			cPickle.dump(data_ring, open("aire_data.cpk","w"))
			cPickle.dump(nk, open("aire_keys.cpk","w"))
			t0 = time()
		else:
			#sleep	
			sleep(1)
			print "[-_-]: ",asctime()
	# end while