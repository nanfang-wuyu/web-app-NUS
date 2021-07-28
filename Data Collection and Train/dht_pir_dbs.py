
import sqlite3
import time
from gpiozero import MotionSensor
import RPi.GPIO as GPIO
import Adafruit_DHT
import IR


RED = 23
GREEN = 24
BLUE = 25
status = 0

# Open SQLite database and create a cursor for later queries.
conn = sqlite3.connect('dht.db')
c = conn.cursor()
pir = MotionSensor(17)
moved = 0


# Main loop to read each sensor and save the readings in the database.
print('Saving sensor data every two seconds (press Ctrl-C to quit)...')
while True:
    # Save the current unix time for this measurement.
    reading_time = int(time.time())
    # Go through each sensor and take a reading.
    if pir.motion_detected:
        print("You moved")
        moved = 1
    else:
        print(0)
        moved = 0
        
    # for s in sensors:
    devicename, dht_type, pin = 'DHT1',Adafruit_DHT.DHT11,4

    humidity, temperature = Adafruit_DHT.read_retry(dht_type, pin)
    print('Read sensor: {0} humidity: {1:0.2f}% temperature: {2:0.2f}C'.format(devicename, humidity, temperature))


    # infrared receiver
    IR.setup()

    print("Waiting for infra signal")
    GPIO.wait_for_edge(27, GPIO.FALLING)
    code = IR.on_ir_receive(27)
    if code:
        status = IR.mode(code,status)
        # print(str(hex(code)))
    else:
        print("No code")
    IR.rgb(status)
    print(status)
    
    # Save the reading in the readings table.
    c.execute("""INSERT INTO readings ('reading_time', 'devicename', 'humidity', 'temperature','moved','label') VALUES (?, ?, ?, ?, ?,?)""",
                (reading_time, devicename, humidity, temperature,moved,status))
    conn.commit()

    time.sleep(0.1)