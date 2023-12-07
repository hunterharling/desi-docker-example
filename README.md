## A Docker container for development with DESI's public S3 bucket

This container has relevant desi packages installed, including desispec, fitsio, and astropy.

# To build and run the container:

```
sudo docker build -t desi-image .
sudo docker run --name desi-container desi-image
```
