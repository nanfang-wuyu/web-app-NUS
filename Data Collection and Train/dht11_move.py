import sqlite3



def read():

    data = []
    
    conn = sqlite3.connect('dht.db')
    c = conn.cursor()
    c.execute('SELECT reading_time, humidity , temperature,  moved  FROM readings ')
    results = c.fetchall()
    print(results)
    
    for result in results:
        data.append({'reading_time':result[0],'Hum':result[1], 'Temp': result[2],'moved': result[2]})

    conn.close()

    return data

