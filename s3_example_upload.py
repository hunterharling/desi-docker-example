
BUCKET_NAME = 'desi-us-east-2'
REGION = 'us-east-2'

import boto3
from botocore.exceptions import NoCredentialsError

def upload_file_to_s3_if_not_exists(file_path, bucket_name, s3_path):
    s3_client = boto3.client('s3')

    try:
        # Check if the file already exists
        try:
            s3_client.head_object(Bucket=bucket_name, Key=s3_path)
            print(f"File already exists at {s3_path} in bucket {bucket_name}.")
            return
        except:
            # File does not exist, so upload it
            s3_client.upload_file(file_path, bucket_name, s3_path)
            print(f"File uploaded to {s3_path} in bucket {bucket_name}.")
    except Exception as e:
        print(e)

# Example usage
files_to_upload = ['/global/cfs/cdirs/desi/public/edr/spectro/redux/fuji/zcatalog/zall-pix-fuji.fits']

for file in files_to_upload:
    upload_file_to_s3_if_not_exists(file, BUCKET_NAME, file.split('global/')[1])
