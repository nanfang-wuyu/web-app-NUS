# export FLASK_APP=try.py
# python3 -m flask run --host=0.0.0.0
# flask run -h localhost -p 3000

import sqlite3
import io
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, render_template, send_file, make_response, request, json

import socket

import requests

import threading

import IR
app = Flask(__name__)


# Retrieve data from database

conn = sqlite3.connect('dht.db', check_same_thread=False)
# c = conn.cursor()
lock = threading.Lock()

import _thread as thread




def getHistData (numSamples):

    c = conn.cursor()
    lock.acquire(True)
    c.execute("SELECT reading_time, temperature, humidity FROM readings ORDER BY reading_time DESC LIMIT "+str(numSamples))
    data = c.fetchall()
    dates = []
    temps = []
    hums = []
    for row in reversed(data):
        dates.append(row[0])
        temps.append(row[1])
        hums.append(row[2])
    conn.commit()
    lock.release()
    c.close()
    # conn.close()
    return dates, temps, hums

def maxRowsTable():

    c = conn.cursor()
    for row in c.execute("select COUNT(temperature) from  readings"):
        maxNumberRows=row[0]

    conn.commit()
    c.close()
    return maxNumberRows
    # define and initialize global variables

global numSamples
numSamples = maxRowsTable()
if (numSamples > 101):
	numSamples = 100
# c.close()
# conn.close()

# main route 
@app.route("/")
def index():	
    
    
    # print("database open")
    time, temp, hum ,moved,label= getLastData()
    templateData = {
        'time': time,
        'temp': temp,
        'hum': hum,
        'moved':moved,
        'label':int(label)
    }
    print(templateData)
    return render_template('index_gage.html', **templateData)

@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples
    numSamples = int (request.form['numSamples'])
    numMaxSamples = maxRowsTable()
    if (numSamples > numMaxSamples):
        numSamples = (numMaxSamples-1)
    time, temp, hum,moved,label = getLastData()
    templateData = {
	  	'time'	: time,
        'temp'	: temp,
        'hum'	: hum,
        'numSamples'	: numSamples
			  
	}
    return render_template('index_gage.html', **templateData)

@app.route('/plot/temp')
def plot_temp():
	times, temps, hums = getHistData(numSamples)
	ys = temps
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Temperature [°C]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/hum')
def plot_hum():
	times, temps, hums = getHistData(numSamples)
	ys = hums
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Humidity [%]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/results', methods=['POST'])
def login():
    data = {"some_key":"some_value"} # Your data in JSON-serializable type
    response = app.response_class(response=json.dumps(data),
                                  status=200,
                                  mimetype='application/json')
    return response

def sendCommand(Prediction):
    
    command = 'error'

    print("Prediction: ", Prediction)
    # print(type(Prediction)) 
    
    if Prediction == 'Unknown':
            
        command = 'unknown'
    
    elif Prediction == '0':
        
        command = '0'
    
    elif Prediction == '1':
        
        command = '1'
    elif Prediction == '2':
        
        command = '2'

    elif Prediction == '3':
        
        command = '3'
        
    host = socket.gethostname()
    # print("sendCommandhost: ", host)
    port = 8888
    # try:
    s = socket.socket()
    s.connect((host, port))
    s.send(command.encode('utf-8'))
    s.close()
    # except socket.error as socketerror:
    #     print("Error: ", socketerror)   


def predictRain(temp, humidity, moved):
    
    base_uri = 'http://169.254.58.193:5000/'
    # base_uri = 'http://169.254.47.65:5000/' 
    predict_uri = base_uri + 'api/predictlabel'
    
    response = requests.get(predict_uri + '?temp=' + str(temp) + '&humidity=' + str(humidity)+'&moved=' + str(moved))

    print("temp: {}, humidity: {}, moved: {}, prediction: {}".format(temp, humidity, moved, response.text))
    
    return response.text.replace('"', '').strip()
    


@app.route('/raspberry')
def rasp():

    conn_2 = sqlite3.connect('dht.db')
    c_2 = conn_2.cursor()
    c_2.execute('SELECT id, devicename, reading_time, temperature, humidity, moved, label,tocloud FROM readings ORDER BY devicename ASC, reading_time DESC')
    results = c_2.fetchall()
    firstRow = None
    
    if len(results) > 0:
        
        firstRow = list(results[0])
        
        
    htmlTableRows = ''
            
        
    for result in results:
                
        htmlTableRows += '<tr><td>' + str(result[0]) + '</td><td>' + str(result[1]) + '</td><td>' + str(result[2]) + '</td><td>' + str(result[3]) + '</td><td>' + str(result[4]) + '</td><td>' + str(result[5]) + '</td><td>' + str(result[6]) + '</td><td>' + str(result[7]) +  '</td></tr>'
    
    c_2.close()
    conn_2.close()
    
    html = '<html><head><title>Edge Processor</title><meta http-equiv="refresh" content="10" /></head><body>'
    html += '<h1>Latest Sensor Data</h1><table width="100%" cellspacing="1" cellpadding="3" border="1">'
    
    if firstRow != None:
        
        # Prediction = predictRain(firstRow[3], firstRow[4],firstRow[5]) # 'Unknown'
        
        # sendCommand(Prediction)  

        html += '<tr><th>ID</th><td>' + str(firstRow[0]) + '</td></tr><tr><th>Device Name</th><td>' + str(firstRow[1]) + '</td></tr><tr><th>Timestamp</th><td>' + str(firstRow[2]) + '</td></tr><tr><th>Temperature</th><td>' + str(firstRow[3]) + '</td></tr><tr><th>Humidity</th><td>' + str(firstRow[4]) + '</td></tr><tr><th>Moving People</th><td>' + str(firstRow[5]) + '</td></tr><tr><th>Model Prediction</th><td>' + str(firstRow[6]) + '</td></tr>'
        
    else:
        
        html += '<tr><th>No Data</th></tr>'
    
    html += '</table><hr />'
    html += '<h1>Historical Sensor Data</h1><table width="100%" cellspacing="1" cellpadding="3" border="1"><tr><th>ID</th><th>Device Name</th><th>Timestamp</th><th>Temperature</th><th>Humidity</th><th>Moving People</th><th>Model</th><th>To Cloud</th></tr>' + htmlTableRows + '</table></body></html>'        
    
    return html

def getLastData():


    conn = sqlite3.connect('dht.db', check_same_thread=False)
    c = conn.cursor()
    
    # lock.acquire(True)
    c.execute('SELECT id, devicename, reading_time, temperature, humidity, moved, label,tocloud FROM readings ORDER BY devicename ASC, reading_time DESC')
    results = c.fetchall()
    # print(row)
    firstRow = list(results[1])
    time = firstRow[2]
    temp = firstRow[3]
    hum = firstRow[4]
    moved = firstRow[5]
    label=firstRow[6]
    # lock.release()
    conn.commit()
    c.close()
    conn.close()
    return time, temp, hum,moved,label

import time

def prediction_thread():
    while True:
        time.sleep(1)
        conn = sqlite3.connect('dht.db', check_same_thread=False)
        c = conn.cursor()
        lock.acquire(True)
        c.execute('select * from readings where reading_time = (select MAX(reading_time) from readings)')
        firstRow = list(c.fetchone())
        # firstRow = None

        if firstRow:
            
            Prediction = predictRain(firstRow[4], firstRow[3], firstRow[5]) # temp, hum, move
            print("Prediction: ", Prediction)
            sendCommand(Prediction)

            firstRow[6] = float(Prediction)

            c.execute('UPDATE readings set label = {} where id = {}'.format(firstRow[6], firstRow[0]))

            print("-------------------------------------------")
            print(Prediction)
            print(firstRow)
            print("Prediction done!")
            conn.commit()
        lock.release()
        c.close()
        conn.close()
    
thread.start_new_thread(prediction_thread, ())

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=6000, debug=False)
	# app.run(host='127.0.0.1', port=6000, debug=False)
	

