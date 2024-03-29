# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container to /app
WORKDIR /app

# Install libbz2-dev (needed for fitsio)
RUN apt-get update && apt-get install -y \
    libbz2-dev \
    git \
    wget \
    fuse \
    libfuse2 \
    && rm -rf /var/lib/apt/lists/*

# Install Mountpoint for Amazon S3
RUN wget https://s3.amazonaws.com/mountpoint-s3-release/latest/x86_64/mount-s3.deb \
    && apt-get install -y ./mount-s3.deb \
    && rm ./mount-s3.deb

# Clone and install desiutil
RUN git clone https://github.com/desihub/desiutil.git && \
    cd desiutil && \
    python setup.py install

# Clone and install desitarget
RUN git clone https://github.com/desihub/desitarget.git && \
    cd desitarget && \
    python setup.py install

# Clone and install desisim
RUN git clone https://github.com/desihub/desisim.git && \
    cd desisim && \
    python setup.py install

# Clone and install desimodel
RUN git clone https://github.com/desihub/desimodel.git && \
    cd desimodel && \
    python setup.py install

# Clone the desispec repository
RUN git clone https://github.com/desihub/desispec.git

# Set environment variables for Python path
ENV PYTHONPATH "${PYTHONPATH}:/app/desiutil/py:/app/desitarget/py:/app/desisim/py:/app/desispec/py:/app/desimodel/py"
ENV PATH "${PATH}:/app/desiutil/bin:/app/desitarget/bin:/app/desisim/bin:/app/desispec/bin:/app/desimodel/bin"

# Install desispec
RUN cd desispec && python setup.py install --prefix=/app/desispec

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fitsio --upgrade --ignore-installed
RUN pip install speclite
RUN pip install numba

# mountpoint
RUN mkdir s3
# RUN mount-s3 desi-us-east-2 ./s3

#CMD ["python", "./test-retry.py"]
