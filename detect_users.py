import boto3
import io
import math
import re
from PIL import Image, ImageDraw, ImageFont

def image_to_byte_array(image, format) -> bytes:
  imgByteArr = io.BytesIO()
  image.save(imgByteArr, format=format)
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr

# This method uses Rekogntion to search against a collection of user vectors
def detect_users_in_image(bucket, key, collection_id, threshold=80):

    session = boto3.Session()
    client = session.client('rekognition')

    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')
    s3_object = s3_connection.Object(bucket, key)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image = Image.open(stream)

    # Call DetectFaces to find faces in image
    response = client.detect_faces(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        Attributes=['ALL']
    )

    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # Calculate and display bounding boxes for each detected face
    for faceDetail in response['FaceDetails']:
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')

        box = faceDetail['BoundingBox']
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']

        print('Left: ' + '{0:.0f}'.format(left))
        print('Top: ' + '{0:.0f}'.format(top))
        print('Face Width: ' + "{0:.0f}".format(width))
        print('Face Height: ' + "{0:.0f}".format(height))

        points = (
            (left, top),
            (left + width, top),
            (left + width, top + height),
            (left, top + height),
            (left, top)
        )

        # Crop the face box and convert it to byte array
        face = image.crop((left, top, left + width, top + height))
        imgByteArr = image_to_byte_array(face, image.format)

        # Search for a user in our collection using the cropped image
        user_response = client.search_users_by_image(
            CollectionId=collection_id,
            Image={'Bytes': imgByteArr},
            UserMatchThreshold=threshold
        )
        # print (user_response)

        # Extract user id and the similarity from the response
        if (user_response['UserMatches']):
            similarity = user_response['UserMatches'][0]['Similarity']
            similarity = (math.trunc(similarity * 100) / 100) if isinstance(similarity, float) else similarity
            user_id = user_response['UserMatches'][0]['User']['UserId']
            print(f"User {user_id} was found, similarity of {similarity}%")
            print("")
        else:
            user_id = "Unknown"
            similarity = 0

        draw.line(points, fill='#00d400', width=4)
        font = ImageFont.load_default(size=25)
        draw.text((left, top - 30), user_id, fill='#00d400', font=font)
        if similarity > 0:
            draw.text((left, top + 1), str(similarity), fill='#00d400', font=font)

    return image

# This method uses Rekogntion **without** user vectors to search against a collection of individual face vectors
def detect_faces_in_image(bucket, key, collection_id, threshold=80):

    session = boto3.Session()
    client = session.client('rekognition')

    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')
    s3_object = s3_connection.Object(bucket, key)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image = Image.open(stream)

    # Call DetectFaces to find faces in image
    response = client.detect_faces(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        Attributes=['ALL']
    )

    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # Calculate and display bounding boxes for each detected face
    for faceDetail in response['FaceDetails']:
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')

        box = faceDetail['BoundingBox']
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']

        print('Left: ' + '{0:.0f}'.format(left))
        print('Top: ' + '{0:.0f}'.format(top))
        print('Face Width: ' + "{0:.0f}".format(width))
        print('Face Height: ' + "{0:.0f}".format(height))

        points = (
            (left, top),
            (left + width, top),
            (left + width, top + height),
            (left, top + height),
            (left, top)
        )

        # Crop the face box and convert it to byte array
        face = image.crop((left, top, left + width, top + height))
        imgByteArr = image_to_byte_array(face, image.format)

        # Search for face in our collection using the cropped image
        response=client.search_faces_by_image(
            CollectionId=collection_id,
            Image={'Bytes': imgByteArr},
            FaceMatchThreshold=threshold
        )
                                
        faceMatches=response['FaceMatches']
        print ('Matching faces:')
        for match in faceMatches:
                similarity = match['Similarity']
                similarity = (math.trunc(similarity * 100) / 100) if isinstance(similarity, float) else similarity
                ExternalImageId = match['Face']['ExternalImageId']
                print(f"FaceId: {match['Face']['FaceId']}, Similarity: {str(similarity)}%, ExternalImageId: {ExternalImageId}")
        
        # Extract details from the response
        if (response['FaceMatches']):
            similarity = response['FaceMatches'][0]['Similarity']
            similarity = (math.trunc(similarity * 100) / 100) if isinstance(similarity, float) else similarity
            ExternalImageId = response['FaceMatches'][0]['Face']['ExternalImageId']
            user_id = re.sub(r'\d.*', '', ExternalImageId)
            # user_id = user_response['UserMatches'][0]['User']['UserId']
            print(f"User {user_id} was found, similarity of {similarity}%")
            print("")
        else:
            user_id = "Unknown"
            similarity = 0

        draw.line(points, fill='#00d400', width=4)
        font = ImageFont.load_default(size=25)
        draw.text((left, top - 30), user_id, fill='#00d400', font=font)
        if similarity > 0:
            draw.text((left, top + 1), str(similarity), fill='#00d400', font=font)

    return image