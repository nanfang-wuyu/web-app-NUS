# export FLASK_APP=aiot-edge.py
# python3 -m flask run --host=0.0.0.0

from flask import Flask

import sqlite3

import socket

import requests

import IR

app = Flask(__name__)



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


def predictRain(temp, humidity,moved):
    
    base_uri = 'http://169.254.58.193:5000/'
    predict_uri = base_uri + 'api/predictlabel'
    
    response = requests.get(predict_uri + '?temp=' + str(temp) + '&humidity=' + str(humidity)+'&moved=' + str(moved))

    print("temp: {}, humidity: {}, moved: {}, prediction: {}".format(humidity, temp, moved, response.text))
    
    return response.text.replace('"', '').strip()
    


@app.route('/')
def index():

    conn = sqlite3.connect('dht.db')
    c = conn.cursor()
    c.execute('SELECT id, devicename, reading_time, temperature, humidity, moved, label,tocloud FROM readings ORDER BY devicename ASC, reading_time DESC')
    results = c.fetchall()
    firstRow = None
    
    if len(results) > 0:
        
        firstRow = list(results[0])

        # Prediction = predictRain(firstRow[3], firstRow[4],firstRow[5]) # 'Unknown'
        Prediction = predictRain(firstRow[4], firstRow[3],firstRow[5]) # 'Unknown'
        
        sendCommand(Prediction)

        firstRow[6] = float(Prediction)

        results[0] = tuple(firstRow)

        c.execute('UPDATE readings set label = {} where id = {}'.format(firstRow[6], firstRow[0]))

        print("__________________________")
        print(Prediction)
        print(firstRow)
        print(results[0])
        print(results[0][6])
        print("__________________________")
        
        
    htmlTableRows = ''
            
        
    for result in results:
                
        htmlTableRows += '<tr><td>' + str(result[0]) + '</td><td>' + str(result[1]) + '</td><td>' + str(result[2]) + '</td><td>' + str(result[3]) + '</td><td>' + str(result[4]) + '</td><td>' + str(result[5]) + '</td><td>' + str(result[6]) + '</td><td>' + str(result[7]) +  '</td></tr>'
    
    c.close()
    conn.close()
    
    html = '<html><head><title>Edge Processor</title><meta http-equiv="refresh" content="10" /></head><body>'
    html += '<h1>Latest Sensor Data</h1><table width="100%" cellspacing="1" cellpadding="3" border="1">'
    
    if firstRow != None:
        
        # Prediction = predictRain(firstRow[3], firstRow[4],firstRow[5]) # 'Unknown'
        
        # sendCommand(Prediction)  
        # IR.rgb(Prediction)    
          
        # c = conn.cursor()
        # c.execute('SELECT id, devicename, reading_time, temperature, humidity, moved, label,tocloud FROM readings ORDER BY devicename ASC, reading_time DESC')
        # results = c.fetchall()

        html += '<tr><th>ID</th><td>' + str(firstRow[0]) + '</td></tr><tr><th>Device Name</th><td>' + str(firstRow[1]) + '</td></tr><tr><th>Timestamp</th><td>' + str(firstRow[2]) + '</td></tr><tr><th>Temperature</th><td>' + str(firstRow[3]) + '</td></tr><tr><th>Humidity</th><td>' + str(firstRow[4]) + '</td></tr><tr><th>Moving People</th><td>' + str(firstRow[5]) + '</td></tr><tr><th>Model Prediction</th><td>' + Prediction + '</td></tr>'
        
    else:
        
        html += '<tr><th>No Data</th></tr>'
    
    html += '</table><hr />'
    html += '<h1>Historical Sensor Data</h1><table width="100%" cellspacing="1" cellpadding="3" border="1"><tr><th>ID</th><th>Device Name</th><th>Timestamp</th><th>Temperature</th><th>Humidity</th><th>Moving People</th><th>Model</th><th>To Cloud</th></tr>' + htmlTableRows + '</table></body></html>'        
    
    return html
