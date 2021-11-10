#Deriving the latest base image
FROM python:latest

WORKDIR /usr/app/src

#to COPY the remote file at working directory in container
COPY feed-me-mensa-ul.py ./
COPY requirements.txt ./

RUN pip install -r requirements.txt


CMD [ "python", "./feed-me-mensa-ul.py"]