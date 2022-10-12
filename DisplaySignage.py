# -- coding: utf-8 --
"""
Created on Mon Sep 12 16:22:22 2022

@author: RSeelam
"""

#activate imageAnalytics
import os
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import uuid
import boto3
import sys
import os,webbrowser
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
#package for deleting the files/Folder inside a folder
import shutil
os.getcwd()
from configparser import ConfigParser
from pathlib import Path
  
# total arguments
n = len(sys.argv)
print("Total arguments passed:", n)
 
# Arguments passed
print("\nName of Python script:", sys.argv[0])
# print("\nName of Python script:", sys.argv[1])
print("\nArguments passed:", end = " ")
# file_name=sys.argv[1]
#sys.exit(1)
configur = ConfigParser()
print (configur.read('config.ini'))

#print(configur.get('server','access_key_id'))

access_key_id = configur.get('server','access_key_id')
secret_access_key=configur.get('server','secret_access_key')
parent_dir=configur.get('installation','parent_dir')
Input_image_path=configur.get('installation','Input_image_path')
directory=configur.get('installation','directory')

confidence_percnet=configur.get('installation','confidence_percnet')
not_needed_attribute_list=configur.get('installation','not_needed_attribute_list')
#file_name = configur.get('installation','file_name')
print(access_key_id)
print(secret_access_key)
print(parent_dir)
print(Input_image_path)
print("direcrour is ",directory)
print(not_needed_attribute_list)
# print(file_name)

#################Below functions are related to master table creations

client = boto3.client('rekognition', 'us-east-1', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)


def getItemsInImage(image,confidence_percnet):
    items_on_person_list = []
    with open(image, 'rb') as image:
        response = client.detect_labels(Image={'Bytes': image.read()})

    labels = response['Labels']
    print(f'Found {len(labels)} labels in the image:')
    for label in labels:
        name = label['Name']
        confidence = label['Confidence']
        if confidence > confidence_percnet and name not in not_needed_attribute_list:
            #print("confidence is ",confidence)
            #print(f'> Label "{name}" with confidence {confidence:.2f}')
            items_on_person_list.append(name)
            #print(name)
    return items_on_person_list

#Funtion for getting the highest confidence emotions
def get_higest_emotion(Emotions_list):
    my_dict = {"Person_ID":[],"Emotion Type":[],"Confidence":[]};
    for label in  Emotions_list:
        unique_id = uuid.uuid4()
        #print(label)
        #print(label[0]["Type"],label[0]["Confidence"])
        my_dict["Person_ID"].append(unique_id)
        my_dict["Emotion Type"].append(label[0]["Type"])
        my_dict["Confidence"].append(label[0]['Confidence'])


    df = pd.DataFrame.from_dict(my_dict)
    newdf=df.groupby('Person_ID')['Confidence'].max().reset_index().sort_values(['Confidence'], ascending=False)
    newdf2=newdf.merge(df, on=['Confidence','Person_ID'], how='left')
    #print(newdf2)
    #print("********************")
    return newdf2

# folder path
#dir_path = r'C:\Users\rseelam\My Python Files\Images\Croped'
def number_of_ppl(dir_path):
    count = 0
    # Iterate directory
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            count += 1
    print('Number of people spotted on Image is :', count , " People")
    return "Success"

#For extracting Age and Gender
def get_age_n_gender(detect_faces):
    AgeRange_dict= {}
    Gender_Dict = {}
    for label in detect_faces['FaceDetails']:
        #print(label)
        #print("_____________****____________")
        AgeRange_dict=label['AgeRange']
        Gender_Dict=label['Gender']
        #print(label['AgeRange'])

    #print("Age of the person is ",AgeRange_dict)
    #print("Gender of the person is ",Gender_Dict)
    return AgeRange_dict,Gender_Dict

#For Opening image in browser
def open_image_in_browser(path):
    iexplore = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                            "Internet Explorer\\IEXPLORE.EXE")
    browser = webbrowser.get(iexplore)
    browser.open(path)
    return "Success"



def raj(file_name):
    print("Hello World!")
    os.chdir(Input_image_path)
    cropped_path = os.path.join(parent_dir, directory)
    print(os.path.exists(cropped_path))
    if os.path.exists(cropped_path) != False:
        shutil.rmtree(cropped_path)
    #print(isExist)
    
    os.mkdir(cropped_path)
    img = Image.open(file_name)
    items_on_frame_list=getItemsInImage(file_name,int(confidence_percnet))
    client = boto3.client('rekognition', 'us-east-1', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
    with open(file_name, 'rb') as im:
        # Read image bytes
        im_bytes = im.read()
        # Upload image to AWS 
        response = client.detect_labels(Image={'Bytes': im_bytes})
        # Get default font to draw texts
        image = Image.open(io.BytesIO(im_bytes))
        image_bckup=Image.open(io.BytesIO(im_bytes))
        font = ImageFont.truetype('arial.ttf', size=80)
        draw = ImageDraw.Draw(image)
        # Get all labels
        w, h = image.size
        for label in response['Labels']:
            name = label['Name']
            # Draw all instancex box, if any
            for instance in label['Instances']:
                bbox = instance['BoundingBox']
                x0 = int(bbox['Left'] * w) 
                y0 = int(bbox['Top'] * h)
                x1 = x0 + int(bbox['Width'] * w)
                y1 = y0 + int(bbox['Height'] * h)
                draw.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=10)
                draw.text((x0, y1), name, font=font, fill=(255, 0, 0))
                #img = img.open(file_name)
                cropped = image_bckup.crop( ( x0, y0, x1 , y1 ) ) 
                unique_id = uuid.uuid4()
                #image_path = r'C:\Users\rseelam\My Python Files\Images\Cropped'
                #os.remove(image_path)
    
                os.chdir(cropped_path)
                #shutil.rmtree(image_path)
                #print(os.getcwd())
                cropped.save('crop'+str(unique_id)+'.jpg')
                
                ##################Below code is for business logic
                
                num_of_ppl_lst = []
                
                if os.path.exists(cropped_path) != False:
                    print(os.path.exists(cropped_path))
                    
                os.chdir(cropped_path)
                #number_of_ppl(cropped_path)
                # iterate over files in
                # that directory
                #PRJSA : below is the for loop for corpped images 
                my_main_list= []
                for filename in os.listdir(cropped_path):
                    #print(filename)
                    my_test_data = []
                    f = os.path.join(cropped_path, filename)
                    #PRJSA: f contains the cropped image with complete path.
                    #print(f)
                    # checking if it is a file
                    if os.path.isfile(f):
                        img = mpimg.imread(f)
                        #imgplot = plt.imshow(img)
                        #plt.show()
                        photo = f
                        with open(photo, 'rb') as image_file:
                            #print("Person X: Below are the characteristics")
                            #getItemsInImage(photo)
                            source_bytes = image_file.read()
                            detect_faces = client.detect_faces(Image={'Bytes': source_bytes},Attributes =['ALL'])
                            #print(detect_faces)
                            Emotions_list= []
                            for label in detect_faces['FaceDetails']:
                
                                #Emotions_list=label['Emotions']
                                Emotions_list.append(label['Emotions'])
                            #print(Emotions_list)
                            
                            age,gender=get_age_n_gender(detect_faces)
                            #print(age)
                            #print(age['Low'])
                            #print(age['High'])
                            
                            if len(age) != 0:                
                                #sys.exit(1)
                                age_range = str(age['Low'])+" to "+str(age['High'])
                                age_mode = (age['Low']+age['High'])/2
                                Adult_or_kid= ''
                                if age_mode >= 20:
                                    Adult_or_kid = 'Adult'
                                else:
                                    Adult_or_kid = 'Kid'
                                num_of_ppl_lst.append(40)
                                ret_df=get_higest_emotion(Emotions_list)
                                Highest_Emotion_Type=ret_df['Emotion Type'].values[:1][0]
                                items_on_person_list=getItemsInImage(photo,int(confidence_percnet))
                                gender_val =  gender['Value']
                                #print(age_range)
                                #print(gender_val)            
                                my_test_data.append(photo)
                                my_test_data.append(gender_val)
                                my_test_data.append(age_range)
                                my_test_data.append(age_mode)
                                my_test_data.append(Adult_or_kid)
                                my_test_data.append(Highest_Emotion_Type)
                                my_test_data.append(items_on_person_list)
                                my_test_data.append(items_on_frame_list)
                                #print(my_test_data)
                                #print(gender) ,'Highest_emotion'
                
                                head1 = ['Image_Key','Gender','Age','age_mode','Adult_or_kid','Highest_Emotion',"items_on_person_list","items_on_frame_list"]
                                d = dict(zip(head1,my_test_data))
                                my_main_list.append(d)
                                
                #print(my_main_list)
                print("Total Number of People in the Frame is ",str(len(num_of_ppl_lst)))
                df = pd.DataFrame(my_main_list)
                print(df)
                df.to_csv(r'C:\Users\zmohiyuddin\Desktop\HARMAN\Projects\Display Signage\Setup\ImageAnalysis.csv', index = False)
                #Write your code : update query
                #######################Below code is for creating the required fields in tabular format
                
                Adult_count=0
                kid_count=0
                df_test=df.groupby(['Adult_or_kid'])['Adult_or_kid'].count().reset_index(name='count')
                
                male_count=female_count=0
                try:
                    Adult_count=df_test.loc[df_test['Adult_or_kid'] == 'Adult', 'count'].values[0]
                except IndexError:
                    Adult_count= 0
                
                try:
                    Kid_count=df_test.loc[df_test['Adult_or_kid'] == 'Kid', 'count'].values[0]
                    
                except IndexError:
                    print("Exception occured no Kid" )
                    Kid_count= 0  
                df['kid_count']=Kid_count    
                df['Adult_count']=Adult_count
                
                
                ##################For adding male count and female count
                male_count=female_count=0
                male_female_Df=df.groupby(['Gender'])['Gender'].count().reset_index(name='count')
                #print(male_female_Df)
                #sys.exit(1)
                
                try:
                    male_count=male_female_Df.loc[male_female_Df['Gender'] == 'Male', 'count'].values[0]
                except IndexError:
                    male_count= 0
                
                try:
                    female_count=male_female_Df.loc[male_female_Df['Gender'] == 'Female', 'count'].values[0]
                    
                except IndexError:
                    print("Exception occured no Female" )
                    female_count= 0  
                    
                    
                
                df["male_count"]=male_count
                df["female_count"]=female_count
                df["group_by_key"]="ABC"
                
                ################Below section is for adding Male Kid count and Female Kid count
                df['Male_kid_Count'] = np.where((df['Adult_or_kid']== 'Kid') & (df['Gender']== 'Male'), 1,0 )
                df['Female_kid_Count'] = np.where((df['Adult_or_kid']== 'Kid') & (df['Gender']== 'Female'), 1,0 )
                df['Adult_Male_Count'] = np.where((df['Adult_or_kid']== 'Adult') & (df['Gender']== 'Male'), 1,0 )
                df['Adult_Female_Count'] = np.where((df['Adult_or_kid']== 'Adult') & (df['Gender']== 'Female'), 1,0 )
                Male_kid_Count_Df=df.groupby(['group_by_key'])['Male_kid_Count'].sum().reset_index(name='sum')
                Female_kid_Count_Df=df.groupby(['group_by_key'])['Female_kid_Count'].sum().reset_index(name='sum')
                Adult_Male_Count_Df=df.groupby(['group_by_key'])['Adult_Male_Count'].sum().reset_index(name='sum')
                Adult_Female_Count_Df=df.groupby(['group_by_key'])['Adult_Female_Count'].sum().reset_index(name='sum')
                Male_kid_Count=Male_kid_Count_Df.loc[Male_kid_Count_Df['group_by_key'] == 'ABC', 'sum'].values[0]
                Female_kid_Count=Female_kid_Count_Df.loc[Female_kid_Count_Df['group_by_key'] == 'ABC', 'sum'].values[0]
                Adult_Male_Count=Adult_Male_Count_Df.loc[Adult_Male_Count_Df['group_by_key'] == 'ABC', 'sum'].values[0]
                Adult_Female_Count=Adult_Female_Count_Df.loc[Adult_Female_Count_Df['group_by_key'] == 'ABC', 'sum'].values[0]
                df.drop(['Male_kid_Count', 'Female_kid_Count','Adult_Male_Count','Adult_Female_Count'], axis = 1)
                df['Male_kid_Count']=Male_kid_Count
                df['Female_kid_Count']=Female_kid_Count
                df['Adult_Male_Count']=Adult_Male_Count
                df['Adult_Female_Count']=Adult_Female_Count
                
                
                df['Main_Group'] = np.where((df['Adult_count']>= 1) & (df['kid_count']== 1) & (df['Female_kid_Count']== 1) , 'Family With Female Kid',
                            np.where((df['Adult_count']>= 1) & (df['kid_count']== 1) & (df['Male_kid_Count']== 1) , 'Family With Male Kid',
                             np.where((df['Adult_count']>= 1) & (df['kid_count']== 0)  & (df['male_count']== 0), 'Female Adult Group', 
                            np.where((df['Adult_count']>= 1) & (df['kid_count']== 0 ) & (df['Adult_Female_Count']== 1 ) & (df['Adult_Male_Count']== 1 ), 'Couple',
                            np.where((df['Adult_count']>= 1) & (df['kid_count']>= 2) & (df['Male_kid_Count']== 0)  &  (df['Female_kid_Count']== 2), 'Family With 2 Female Kids',
                            np.where((df['Adult_count']>= 1) & (df['kid_count']>= 2) & (df['Male_kid_Count']== 1)  &  (df['Female_kid_Count']== 1), 'Family With 1 Male and 1 Female Kid',         
                          np.where((df['Adult_count']>= 1) & (df['kid_count']>= 2) & (df['Female_kid_Count']== 0)  &  (df['Male_kid_Count']== 2), 'Family With 2 Male Kids','Others')))))))
                
                
               


    return df 


# if _name_ == "_main_":
#     master_df=main()
#     print(master_df)
    # if master_df.Main_Group.unique()[0] == 'Family With Kids':
    #     open_image_in_browser(r'C:\Users\rseelam\My Python Files\Output_Advertisements\Family_with_kids_Add1.jpg')
    # if master_df.Main_Group.unique()[0] == 'Female Adult Group':
    #     open_image_in_browser(r'C:\Users\rseelam\My Python Files\Output_Advertisements\Female Adult Group Ad.jpg')
    # print("Main code completed")
