# A Docker container for development with DESI's public S3 bucket

This container has relevant desi packages installed, including desispec, fitsio, and astropy.

## Build the container:

1. Create .env File: Make sure you have an .env file in the same directory as your Dockerfile with the AWS credentials. It should look like this:

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

2. Run the Docker build and run commands
```
sudo docker build -t desi-image .
sudo docker run --env-file .env --name desi-container desi-image
```

## Other useful commands

To remove all images and containers (if the you have unused images/containers taking up space on the instance):

```
sudo docker rm -vf $(sudo docker ps -aq)
sudo docker rmi -f $(sudo docker images -aq)
```
