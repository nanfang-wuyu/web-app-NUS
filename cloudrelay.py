import time
import sqlite3
import requests
import json



try:
	conn = sqlite3.connect('dht.db')
	
	# base_uri = 'http://169.254.47.65:5000/' 
	base_uri = 'http://169.254.58.193:5000/' 
	# globaltemperature_uri = base_uri + 'api/globaltemperature'
	predictrain_uri = base_uri + 'api/predictrain'
	headers = {'content-type': 'application/json'}
	
	
	
	while True:
	
		time.sleep(10)
		
		print('Relaying data to cloud server...')
				
		c = conn.cursor()
		c.execute('SELECT id, reading_time, devicename, humidity, temperature, moved,label, tocloud FROM readings WHERE tocloud = 0')
		#c.execute('SELECT id, devicename, temp, timestamp FROM temperature')
		results = c.fetchall()
		c = conn.cursor()
				
		for result in results:
					
			# print('Relaying id={}; devicename={}; temp={}; timestamp={}'.format(result[0], result[1], result[2], result[3]))
			
			gtemp = {
			'reading_time': result[1],
			'devicename': result[2],
			'humidity': result[3],
			'temp': result[4],
			'moved': result[5],
			'label': result[6]
			}

			print(gtemp)
			# req = requests.put(globaltemperature_uri, headers = headers, data = json.dumps(gtemp))
			
			req = requests.get(predictrain_uri, headers = headers, data = json.dumps(gtemp))
			print(req.text)
			c.execute('UPDATE readings SET tocloud = 1 WHERE id = ' + str(result[0]))
		
		conn.commit()



except KeyboardInterrupt:
	
	print('********** END')
	
except Error as err:

	print('********** ERROR: {}'.format(err))

finally:

	conn.close()
