import boto3
import os
from botocore.exceptions import ClientError
session = boto3.Session()
client = session.client('rekognition')

def create_collection(collection_id):
    try:
        # Create a collection
        print('Creating collection:' + collection_id)
        response = client.create_collection(CollectionId=collection_id)
        print('Collection ARN: ' + response['CollectionArn'])
        print('Status code: ' + str(response['StatusCode']))
        print('Done...')
    except client.exceptions.ResourceAlreadyExistsException:
        print('Resource already exits...')
        
def delete_collection(collection_id):
    print('Attempting to delete collection ' + collection_id)
    status_code = 0

    try:
        response = client.delete_collection(CollectionId=collection_id)
        status_code = response['StatusCode']

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print('The collection ' + collection_id + ' was not found ')
        else:
            print('Error other than Not Found occurred: ' + e.response['Error']['Message'])
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']
    return (status_code)

def create_user(collection_id, user_id):
    try:
        print(f'Creating user: {collection_id}, {user_id}')
        client.create_user(
            CollectionId=collection_id,
            UserId=user_id
        )
    except:
        print(f'Failed to create user with given user id: {user_id}')

def add_faces_to_collection(bucket, prefix, collection_id):
    filename = os.path.basename(prefix)
    response = client.index_faces(CollectionId=collection_id,
                                  Image={'S3Object': {'Bucket': bucket, 'Name': prefix}},
                                  ExternalImageId=filename,
                                  MaxFaces=1,
                                  QualityFilter="AUTO",
                                  DetectionAttributes=['ALL'])

    print('Results for ' + prefix)   
    for faceRecord in response['FaceRecords']:
        face_id = faceRecord['Face']['FaceId']
        print('  Face ID: ' + face_id)
    return face_id
        
def associate_faces(collection_id, user_id, face_ids):
    print(f'Associating faces to user: {user_id}, {face_ids}')
    try:
        response = client.associate_faces(
            CollectionId=collection_id,
            UserId=user_id,
            FaceIds=face_ids
        )
        print(f'- associated {len(response["AssociatedFaces"])} faces')
    except:
        print("Failed to associate faces to the given user")
        raise
    else:
        print(response)
        return response
    
def get_subdirs(bucket, prefix):
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter='/')
    subdirs = []
    for page in pages:
        if page.get('CommonPrefixes'):
            for subdir in page['CommonPrefixes']:
                path = subdir['Prefix']
                subdirectory = path.split('/')[-2]
                if not subdirectory.startswith('.'):
                    subdirs.append(subdirectory)
    return subdirs

def get_files(bucket, prefix):
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

    files = []
    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                key = obj["Key"]
                if not key.startswith(".") and not "/." in key:
                    files.append(key)

    return files