import os
import requests

CACHE_DIR = "cache"

def fetch_s3_file(bucket_name, file_key):
    local_path = os.path.join(CACHE_DIR, file_key)
    
    if os.path.exists(local_path):
        print(f"File {file_key} found in cache. No need to fetch again!")
        return local_path
    
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
    response = requests.get(s3_url, stream=True)
    response.raise_for_status()

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"File {file_key} fetched from S3 and saved to cache.")
    return local_path

def main():
    BUCKET_NAME = '__'
    FILE_KEY = '__'  #example: 'path/to/image.fit'
    
    local_file = fetch_s3_file(BUCKET_NAME, FILE_KEY)
    print(f"Local path: {local_file}")

if __name__ == "__main__":
    main()
