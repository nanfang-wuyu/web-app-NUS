from flask import make_response, abort

from joblib import dump, load



def predict(temp, humidity,moved):
	
	try:
		
		# predict new temperature and humidity observation
		clf = load('dht-classifier-4.joblib')

		# temperature, humidity , moved
		newX = [[humidity,temp,moved]]
		result = clf.predict(newX)
		print('Predict Rain: temp={}; humidity={}; moved={}; label={}'.format(temp, humidity, moved,result[0]))

		return str(int(result[0]))
		
	except Exception as error:

		return 'Unknown'
