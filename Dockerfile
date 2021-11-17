FROM python:latest

WORKDIR /usr/app/src

COPY feed-me-mensa-ul.py ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

CMD [ "python", "./feed_me_mensa_ul.py"]