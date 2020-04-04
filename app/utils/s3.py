import boto3
from flask import send_file


def upload_file(data, bucket, name):
    """
    Function to upload a file to an S3 bucket
    """
    s3_client = boto3.client('s3')
    response = s3_client.upload_fileobj(data, bucket, name)
    return response


def download_file(file_name, bucket):
    """
    Function to download a given file from an S3 bucket
    """
    s3 = boto3.resource('s3')

    local_name = file_name.replace(" ", "_")

    current = f"app/downloads/{local_name}"

    output = f"downloads/{local_name}"
    s3.Bucket(bucket).download_file(file_name, current)

    return send_file(output, as_attachment=False)


def list_files(bucket):
    """
    Function to list files in a given S3 bucket
    """
    s3 = boto3.client('s3')
    contents = []
    for item in s3.list_objects(Bucket=bucket)['Contents']:
        contents.append(item)

    return contents
