import json
import boto3
import sys

import sys
sys.path.insert(0, '/tmp/')

import botocore
import os
import subprocess
import cv2
import torch
from PIL import Image

s3 = boto3.resource('s3')


def lambda_handler(event, context):
    print(event)
    #download the image
    image = event["Records"][0]["s3"]["object"]["key"]
    image_key = event["Records"][0]["s3"]["object"]["key"].split('/')
    filename = image_key[-1]
    local_file = '/tmp/'+filename  # Lambda actions needs to be in /tmp
    download_from_s3(image,local_file)
        
    #Detect the image
    results = detect_image(local_file)
    print(results)
    #command = 'python ./yolov5/detect.py --weights {} --img 640 --conf 0.4 --source {} --name test'.format('/tmp/yolo.pt',local_file)
    #try:
     #   print('Start')
      #  output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
       # print('Finish')
       # print(output)
    #except subprocess.CalledProcessError as e:
     #   print('Error')
      #  print(e.output)
    return {
        'statusCode': 200,
        'body': json.dumps({"output":"Lambda execution was successful"})
    }

def download_from_s3(file,object_name):
    try:
        s3.Bucket('statementsoutput').download_file(file,object_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise


def detect_image(local_file):
    filename = local_file.split('.')
    # Model
    s3.Bucket('yolov5weight').download_file('yolo.pt','/tmp/yolo.pt')
      model = torch.hub.load('ultralytics/yolov5', 'custom', path='/tmp/yolo.pt')  # default
    
    #model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
    # Images
    img1 = Image.open(local_file)  # PIL image
    #img2 = cv2.imread('bus.jpg')[:, :, ::-1]  # OpenCV image (BGR to RGB)
    imgs = [img1]  # batch of images
    # Inference
    # If there is a for loop then we will use results
    results = model(imgs, size=640)  # includes NMS
    
    #Cropped-image
    #crops = results.crop()
    # Results
    results.print()
    print(results.pandas().xyxy)
    #crops.save(filename[0]+'_processed.'+filename[1])  # or .show()
    #upload_file(filename[0]+'_processed.'+filename[1])
    
    

#Function to upload files to s3
def upload_file(file_name, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # Upload the file
    try:
        response = s3_client.upload_file(file_name, 'statementsoutput', object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

