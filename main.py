import io
import csv
import cv2
import time
import uuid
import boto3
import threading
import numpy as np
import pandas as pd
from PIL import Image
from statistics import mean, median, mode
from configparser import ConfigParser

# with open('zeeshan_accessKeys.csv', 'r') as input:
#     next(input)
#     reader = csv.reader(input)
#     for line in reader:
#         access_key_id = line[0]
#         secret_access_key = line[1]

df = pd.read_csv('zeeshan_accessKeys.csv')
access_key_id, secret_access_key = df.values[0]
client = boto3.client('rekognition', 'us-east-1', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

def get_data(faces,frame):

    global numPeople, Ad

    if len(faces):
        success, encoded_image = cv2.imencode('.jpg', frame)
        i = encoded_image.tobytes()
        detect_faces = client.detect_faces(Image={'Bytes': i}, Attributes=['ALL'])
        detect_labels = client.detect_labels(Image={'Bytes': i})

        if len(detect_faces['FaceDetails'])>0:
            age_list, gender_list = [], []
            count = len(detect_faces['FaceDetails'])
            numPeople = f'{count} Faces Detected'
            date = detect_faces['ResponseMetadata']['HTTPHeaders']['date']

            for face in range(count):
                gender = detect_faces['FaceDetails'][face]['Gender']['Value']
                ageLow = detect_faces['FaceDetails'][face]['AgeRange']['Low']
                ageHigh = detect_faces['FaceDetails'][face]['AgeRange']['High']
                emotion = detect_faces['FaceDetails'][face]['Emotions'][0]['Type']
                glassess = detect_faces['FaceDetails'][face]['Eyeglasses']['Value']
                beard = detect_faces['FaceDetails'][face]['Beard']['Value']

                person_attr = (date, count, gender, ageLow, ageHigh, emotion, glassess, beard)
                print(f"***PERSON Attributes = {person_attr}",)
                age_list.append((ageLow+ageHigh)/2)
                gender_list.append(gender)
                
                # val1 = (date, count, gender, ageLow, ageHigh, emotion, glassess, beard)
                # mycursor.execute(log_sql, val1)
                # mydb.commit()

            labels = ', '.join([i['Name'] for i in detect_labels['Labels']])
            print(f"***OBJECTS DETECTED = {labels}",)
            
            Ad, ad_loc = recommender(gender_list, age_list)
            # Ads = recommender(gender_list, age_list)
            # Ad, ad_loc = Ads
            print(f"Recommend Advertisement ---> {Ad}")
            
            # val2 = (date, count, labels)
            # mycursor.execute(labels_sql, val2)
            # mydb.commit()
            
            # cv2.
            
            
def recommender(g, a):
    c = {0:['None','Ad/Blank.jpg'],1:['MK','Ad/Dove_MK.jpg'],2:['MA','Ad/Dove_MA.jpg'], 3:['MS','Ad/Dove_MS.jpg'], 10:['FK','Ad/Dove_FK.jpg'], 20:['FA','Ad/Dove_FA.jpg'], 30:['FS','Ad/Dove_FS.jpg']}
    v, m = 0, 1
    if max(g)=='Female': m=10
    if median(a)<10: v+=1
    elif median(a)<50: v+=2
    elif median(a)>=50: v+=3
    return c[m*v]


def main():
    vid = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_TRIPLEX
    start = time.time()
    global numPeople, Ad
    numPeople, Ad = 'Face Detection Started !', 'None'
    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    configur = ConfigParser()
    configur.read('config.ini')
    Input_image_path=configur.get('installation','Input_image_path')

    while(True):
        ret, frame = vid.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        current_time = time.time()

        faces = detector.detectMultiScale(gray, 1.1, 4)
        for (x, y , w ,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255 , 0), 3)
            # roi_gray = gray[y:y+h, x:x+w]
            # roi_color = frame[y:y+h, x:x+w]
        
        if current_time - start >= 3:
            if len(faces):
                t1 = threading.Thread(target=get_data, args=(faces, frame))
                t1.start()
                # t1.join()
                start = current_time
            else:
                numPeople, Ad = 'Face Detection Started !', 'None'
            
            # frame = cv2.putText(frame, f"{numPeople}, \n Ad Category - {Ad}",(5, 20),font, 1,(0, 255, 0),2, cv2.LINE_8)
            frame = cv2.putText(frame, f"{numPeople}",(5, 40),font, 1,(0, 255, 0),2, cv2.LINE_8)
            frame = cv2.putText(frame, f"Ad Category - {Ad}",(5, 80),font, 1,(0, 255, 0),2, cv2.LINE_8)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    vid.release()

if __name__ == "__main__":
    main()