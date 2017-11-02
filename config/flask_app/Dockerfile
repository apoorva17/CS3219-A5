FROM python:3.6
WORKDIR /app

ENV MONGO_HOST mongodb
ENV MONGO_PORT 27017

# Python dependencies
ADD ./requirements.txt /config/requirements.txt
RUN pip install -r /config/requirements.txt
