import time

import sqlite3

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn import metrics
import graphviz

from joblib import dump, load



def main():
	
	print('Starting rain classifier training process')
	
	np.random.seed(int(round(time.time())))

	while True:

		try:         

			conn = sqlite3.connect('dht.db')
			c = conn.cursor()
			c.execute('SELECT reading_time, humidity, temperature, moved,label FROM readings')
			results = c.fetchall()
			
			df = pd.DataFrame(columns=['timestamp', 'humidity', 'temperature', 'moved','label'])
			print(df)

			for result in results:

				df = df.append(
					{'timestamp': str(result[0]), 'humidity': result[1], 'temperature': result[2],'moved': result[3], 'label': result[4]},
					ignore_index=True)

			print(df)
			
			# train a decision tree classifier to predict rain
			random_state = np.random.randint(2**31-1)
			X = df.drop('timestamp', axis=1).drop('label', axis=1).values
			y = df['label'].values
			X_train, X_test, y_train, y_test = train_test_split(X, y, train_size = 0.7, test_size = 0.3, shuffle = True, random_state=random_state, stratify=df['label'])
			X_headers = df.drop('timestamp', axis=1).drop('label', axis=1).columns.values
			
			clf = tree.DecisionTreeClassifier(criterion='gini', splitter='best',max_depth=3)
			clf = clf.fit(X_train, y_train)
			y_train_pred = clf.predict(X_train)

			print('Training Accuracy = {}'.format(metrics.accuracy_score(y_train, y_train_pred)))
			print('Training Confusion = \n{}'.format(metrics.confusion_matrix(y_true=y_train, y_pred=y_train_pred, labels=[0,1,2,3])))
			
			y_test_pred = clf.predict(X_test)
			
			print('Testing Accuracy = {}'.format(metrics.accuracy_score(y_test, y_test_pred)))
			print('Testing Confusion = \n{}'.format(metrics.confusion_matrix(y_true=y_test, y_pred=y_test_pred, labels=[0,1,2,3])))

			# generate the decision tree for visualisation
			dot_data = tree.export_graphviz(clf, out_file=None, feature_names=X_headers, class_names=['0','1','2','3'],
			filled=True, rounded=True, special_characters=True)
			graph = graphviz.Source(dot_data)
			graph.render("dht-train")
			
			# export the classifier model for future use
			dump(clf, 'dht-classifier.joblib')
			
			time.sleep(60)

		except Exception as error:

			print('Error: {}'.format(error.args[0]))
			continue

		except KeyboardInterrupt:

			print('Program terminating...')    
			break



if __name__ == '__main__':
	
	main()
