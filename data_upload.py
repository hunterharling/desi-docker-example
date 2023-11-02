import boto3
import os

def upload_to_s3(bucket_name, root_path):
    s3 = boto3.client('s3')

    for foldername, subfolders, filenames in os.walk(root_path):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)

            s3_key = os.path.relpath(file_path, root_path)

            s3.upload_file(file_path, bucket_name, s3_key)
            print(f"Uploaded {file_path} to {bucket_name}/{s3_key}")

if __name__ == "__main__":
    BUCKET_NAME = '__'
    ROOT_PATH = '__'

    upload_to_s3(BUCKET_NAME, ROOT_PATH)
