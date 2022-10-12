import csv
import cv2
import time
import boto3
import io
from PIL import Image
import threading
import numpy as np
import pandas as pd
import mysql.connector as sql

mydb = sql.connect(host="localhost", 
                   user="root",
                   database='customer_data',
                   passwd="85508Cr7@zee22",
                   auth_plugin='mysql_native_password')

mycursor = mydb.cursor()
log_sql = "INSERT INTO logs (timest, numPeople, gender, ageLow, ageHigh, emotion, glassess, beard)" + \
      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
labels_sql = "INSERT INTO labels_data (timest, numPeople, objects)" + \
      "VALUES (%s, %s, %s)"


with open('zeeshan_accessKeys.csv', 'r') as input:
    next(input)
    reader = csv.reader(input)
    for line in reader:
        access_key_id = line[0]
        secret_access_key = line[1]

client = boto3.client('rekognition', 'us-east-1', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

vid = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_TRIPLEX
start = time.time()
numPeople = 'Face Detection Started'
detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def get_data(frame):
    global numPeople
    if len(detector.detectMultiScale(gray, 1.1, 4)):
        success, encoded_image = cv2.imencode('.jpg', frame)
        i = encoded_image.tobytes()
        detect_faces = client.detect_faces(Image={'Bytes': i}, Attributes=['ALL'])
        detect_labels = client.detect_labels(Image={'Bytes': i})

        if len(detect_faces['FaceDetails'])>0:
            count = len(detect_faces['FaceDetails'])
            numPeople = str(count) + 'Faces Detected'
            date = detect_faces['ResponseMetadata']['HTTPHeaders']['date']
                        
            for face in range(0, count):
                gender = detect_faces['FaceDetails'][face]['Gender']['Value']
                ageLow = detect_faces['FaceDetails'][face]['AgeRange']['Low']
                ageHigh = detect_faces['FaceDetails'][face]['AgeRange']['High']
                emotion = detect_faces['FaceDetails'][face]['Emotions'][0]['Type']
                glassess = detect_faces['FaceDetails'][face]['Eyeglasses']['Value']
                beard = detect_faces['FaceDetails'][face]['Beard']['Value']

                val1 = (date, count, gender, ageLow, ageHigh, emotion, glassess, beard)
                mycursor.execute(log_sql, val1)
                mydb.commit()

            emp_lst = []
            for label in detect_labels['Labels']:
                emp_lst.append(label['Name'])
            labels = ', '.join(emp_lst)
            val2 = (date, count, labels)
            mycursor.execute(labels_sql, val2)
            mydb.commit()

        else:
            numPeople = "No Face Detected !!!!"
    else:
        numPeople = "No Person Detected !!!!"

while(True):
    ret, frame = vid.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    current_time = time.time()

    faces = detector.detectMultiScale(gray, 1.1, 4)
    for (x, y , w ,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255 , 0), 3)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
    
    if current_time - start >= 3:
        t1 = threading.Thread(target=get_data, args=(frame,))
        t1.start()
        # t1.join()
        start = current_time
        
    frame = cv2.putText(frame, str(numPeople),(10, 100),font, 1,(0, 255, 0),4, cv2.LINE_8)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
vid.release()