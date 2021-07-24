import time
from datetime import datetime

import RPi.GPIO as GPIO

import Adafruit_DHT
from gpiozero import MotionSensor
import sqlite3

import socket
import _thread as thread

import requests
import json
import IR


def init():
    
    global RED,GREEN,BLUE

    RED = 23
    GREEN = 24
    BLUE = 25

    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.setup(BLUE, GPIO.OUT)
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    GPIO.output(RED,0)
    GPIO.output(GREEN,0)
    GPIO.output(BLUE,0)

    global pir
    pir = MotionSensor(17)

    global status
    status = 0

    global dbConn
    dbConn = sqlite3.connect('dht.db')



def service_client(client_socket, address):        
    global status
    while True:
        
        data = client_socket.recv(1024).decode('utf-8')
        # print(data)
        if not data:
            break
        
        # print('[Command from {}] {}'.format(str(address), data))
        
        if data == '1':
            
            status = 1

        if data == '2':
            
            status = 2
        if data == '3':
            
            status = 3
        
        elif data == '0':
            
            status = 0

        
    
    client_socket.close()



def listenCommand():
    
    host = socket.gethostname()
    print("listenCommand host: ", host)
    port = 8888

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    
    while True:
        
        s.listen(1)
        client_socket, address = s.accept()            
        thread.start_new_thread(service_client, (client_socket, address))
    
    s.close()



def relaySensorData():
    
    base_uri = 'http://169.254.58.193:5000/'
    globaltemperature_uri = base_uri + 'api/globaltemperature'
    headers = {'content-type': 'application/json'}
    
    while True:
        
        time.sleep(30)
        
        print('[Relaying sensor data to cloud]')
        
        localDbConn = sqlite3.connect('dht.db')
        c = localDbConn.cursor()
        c.execute('SELECT id, reading_time, devicename, humidity, temperature, moved,label, tocloud FROM readings WHERE tocloud = 0')
        results = c.fetchall()
        
        for result in results:
            
            gtemp = {
			'reading_time': result[1],
            'devicename':result[2],
			'humidity': result[3],
			'temp': result[4],
			'moved': result[5],
			'label': result[6]
			}
            
            req = requests.put(globaltemperature_uri, headers = headers, data = json.dumps(gtemp))
			
            c.execute('UPDATE readings SET tocloud = 1 WHERE id = ' + str(result[0]))
                
        c.close()
        localDbConn.commit()
        localDbConn.close()



def saveSensorData(humidity,temperature, moved,status):
    
    c = dbConn.cursor()
    sql = "INSERT INTO readings (devicename, temperature, humidity, moved,label) VALUES('school'," + str(temperature) + ", " + str(humidity) + ", " + str(moved) + ", " + str(status) + ")"
    c.execute(sql)

    dbConn.commit()
    c.close()



def main():
    
    global status

    init()
    
    thread.start_new_thread(listenCommand, ())
    thread.start_new_thread(relaySensorData, ())
    
    print('Program running... Press CTRL+C to exit')
    

    while True:

        try:
            print()
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 4)        
            if pir.motion_detected:
                print("You moved")
                moved = 1
            else:
                print('no move')
                moved = 0
            
            print("Waiting for infra signal")
            # GPIO.wait_for_edge(27, GPIO.FALLING)
            # code = IR.on_ir_receive(27)
            # if code:
            #     status = IR.mode(code,status)
            #     print(str(hex(code)))
            # else:
            #     print("No code")
            print("status: ", status)
            IR.rgb(status)

            print('{}: DHT11: Temperature={}; Humidity={} ; Moving People={}||  Model: {}'.format(datetime.now(), temperature, humidity, moved, status))
            saveSensorData(humidity, temperature,moved,status)

            time.sleep(1)
            
        except RuntimeError:
            
            time.sleep(5)
            
            continue
        
        except Exception as error:
            
            print('Error: {}'.format(error.args[0]))
            continue
            
        except KeyboardInterrupt:
            
            print('Program terminating...')    
            break



    GPIO.cleanup()
    
    if dbConn != None:
        
        dbConn.close()

    print('Program exited...')



if __name__ == '__main__':
    
    main()
