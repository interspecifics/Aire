# -*- coding: utf-8 -*-

"""
*//radar
~same as tides but for
 ·sensor de presión hidrostática PRS 	(WL-K)
 ·sensor radar RAD 						(WL-V)
~estaciones del SHOA
 ·http://www.shoa.cl/nuestros-servicios/mareas?id=811
"""

import requests, cPickle, OSC, sys
from bs4 import BeautifulSoup as BS
from time import localtime, time, sleep, asctime

# --vars
send_period = 1  #s
get_period = 600  #s
n_steps = 100;
#osc_host = "127.0.0.15"
osc_host = "locahost"
osc_port = 57120
#shoa service
stations = ['ARI','PIS','IQQ','PAT','TOC',
			'MEJ','ANT','PAP','TAL','CHN']
url_base = 'http://www.cona.cl/mareas/grafico.php?estacion='

# -- meths
def update_stations():
	""" create queries, fetch data, parse & return data dict"""
	station_dict = {}
	print '+[UPDATING STATIONS DATA]:'
	for st in stations:
		data_dict = {}
		url = url_base + st
		html = requests.get(url).text
		soup = BS(html, "html.parser")
		scripts = soup.find_all('script')
		scraps = [l.text.replace(u'\n',u'').replace(u'\t',u'').strip().rstrip().split(u';') for l in scripts if l.text.find(u'Fecha')>0]
		scraps = scraps[1:-1]
		completed = 0
		for sc in scraps:
			m0 = sc[0].find(u'\"')+1; m1 = sc[0].find(u'\"', m0)
			timestamp = sc[0][m0:m1]
			m0 = sc[1].find(u'\"')+1; m1 = sc[1].find(u'\"', m0)
			data = sc[1][m0:m1]
			m0 = sc[2].find(u'\"')+1; m1 = sc[2].find(u'\"', m0)
			typ = sc[2][m0:m1]
			if (timestamp != u'' and data != u'' and typ != u''):
				try:
					data_dict[typ][0].append(timestamp)
					data_dict[typ][1].append(float(data))
				except:
					data_dict[typ] = [[timestamp],[data]]
				completed+=1
			else:
				print 'Unparseable:' + str(sc)
		station_dict[st] = data_dict
		print '\t\t['+st+']: ' + str(completed)
	print '\t\t\t\tOK :: ' +  asctime()
	return station_dict


def send_actual(i_st, i_po, cOsc):
	"""form and send osc messahe"""
	stat_ion = stations[i_st]
	posit_ion = i_po
	key_s = data_block[stat_ion].keys()
	str_out = "[OSC]: "
	for k in key_s:
		route = "/"+stat_ion+"/"+str(k)
		d = data_block[stat_ion][k][1][i_po]
		msg = OSC.OSCMessage()
		msg.setAddress(route)
		msg.append(d)
		cOsc.send(msg)
		str_out += "\n\t\t%s %.2f" % (route, d)
	return str_out





if __name__ == "__main__":
	# -- parse args
	# --vars
	if (len(sys.argv)>=3):
		send_period = int(sys.argv[1] )
		get_period = int(sys.argv[2])
		n_steps = int(sys.argv[3])
		print "[+.+]: SEND_period=%ds, GET_period=%ds, STEPS_n=%d" % (send_period, get_period, n_steps)

	# -- inits
	i_po = -1;
	i_st = 0
	send_addr = osc_host, osc_port
	cOsc = OSC.OSCClient()
	cOsc.connect(send_addr)
	# -- fetch or load data
	try:
		data_block = update_stations()
		cPickle.dump(data_block, open('radar.data',"w"))
		print "[·-·]: new data"
	except:
		data_block = cPickle.load(open('radar.data', 'r'))
		print "[._.]: old data"

	# -- the loop
	t0 = time()
	while ( True ):
		# -- stream data
		mms = send_actual(i_st, i_po, cOsc)
		print mms

		i_st = i_st+1 if i_st < len(stations)-1 else 0
		if (i_st == 0):
			i_po = i_po-1 if i_po > -n_steps else -1
			print "[T]: %d minutos" % i_po

		# --update
		if ( abs(time()-t0) > get_period ):
			try:
				data_block = update_stations()
				cPickle.dump(data_block, open('radar.data',"w"))
				print "[·-·]: new data"
			except:
				print "[=-=]: same data"
			t0 = time()
		else:
			# --sleep
			sleep(send_period)
	# end whilep