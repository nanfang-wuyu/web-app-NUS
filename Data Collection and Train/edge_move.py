
import connexion
import sqlite3



app = connexion.App(__name__, specification_dir='./')
app.add_api('dht_edge.yml')
  

@app.route('/')
def index():

	conn = sqlite3.connect('dht.db')
	c = conn.cursor()
	c.execute('SELECT reading_time, humidity , temperature,moved  FROM readings ')
	results = c.fetchall()
	
	html = """
	<html>
		<head>
			<title>
				Edge/Fog Processor
			</title>
		</head>
	<body>
	<h1>
		Local Data
	</h1>
	<table cellspacing="1" cellpadding="3" border="1">
		<tr>
			<th>reading_time</th>
			<th>Humidity</th>
			<th>Temperature</th>
			<th>moved</th>
		</tr>"""

	for result in results:
				
		html += \
		'<tr><td>' + str(result[0]) + \
		'</td><td>' + str(result[1]) + \
		'</td><td>' + str(result[2]) + \
		'</td><td>' + str(result[3]) + '</td></tr>'
	
	html += '</body></html>'
	
	conn.close()
	
	return html

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

