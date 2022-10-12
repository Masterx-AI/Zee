import cv2
import boto3

with open('blank.jpg', 'rb') as img:
    s = img.read()
    
# s = cv2.imread('blank.jpg')
# print(type(s))
# s = s.tobytes()
print(type(s))
print(s)

access_key_id = 'AKIAX7KUAIKFFE3IXD2C'
secret_access_key = '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'
client = boto3.client('rekognition', 'us-east-1', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

# d = client.detect_faces(Image={'Bytes': s}, Attributes=['ALL'])
# print(type(d))
# print(d)


