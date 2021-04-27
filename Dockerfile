#
# spyFront Dockerfile
#
#

# Pull base image.
FROM python:3.4.5-slim

# Get some custom packages
RUN apt-get update && apt-get install -y \
    build-essential \
    make \
    gcc \
    python3-dev 

## make a local directory
RUN mkdir /opt/spyFront

# set the working directory from which CMD, RUN, ADD references
WORKDIR /opt/spyFront

# now copy all the files in this directory to /code
ADD . .

# pip install the local requirements.txt
RUN pip install -r requirements.txt

# Listen to port 5000 at runtime
EXPOSE 5003

# start the app server
CMD python manage.py runserver
