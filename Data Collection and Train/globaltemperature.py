#import mysql.connector
import sqlite3
from flask import make_response, abort



def read():
	
	temperatures = []
	
	conn = sqlite3.connect('dht.db')
	
	c = conn.cursor()
	c.execute('SELECT id, reading_time, devicename, humidity, temperature, moved,label FROM readings')
	results = c.fetchall()
	
	for result in results:
				
		temperatures.append({
		'reading_time': result[1],
		'devicename': result[2],
			'humidity': result[3],
			'temp': result[4],
			'moved': result[5],
			'label': result[6]})
	
	conn.close()
	
	return temperatures



def create(globaltemperature):
	'''
	This function creates a new temperature record in the database
	based on the passed in temperature data
	:param globaltemperature:  Global temperature record to create in the database
	:return:        200 on success
	'''
	
	reading_time = globaltemperature.get('reading_time', None)
	devicename = globaltemperature.get('devicename', None)
	humidity = globaltemperature.get('humidity', None)
	temp = globaltemperature.get('temp', None)
	moved = globaltemperature.get('moved', None)
	label = globaltemperature.get('label', None)


	conn = sqlite3.connect('dht.db')
	
	c = conn.cursor()	

	c.execute("""INSERT INTO readings ('reading_time', 'devicename', 'humidity', 'temperature','moved','label') VALUES (?, ?, ?, ?, ?,?)""",
                  (reading_time, devicename, humidity, temp, moved,label))
	print((reading_time, devicename, humidity, temp, moved,label))
	conn.commit()
	conn.close()
	
	
	return make_response('Global temperature record successfully created', 200)
