FROM python:3-alpine

LABEL maintainer="Akanksha Sood akanksha.sood@sesam.io"

RUN apk update

RUN pip install --upgrade pip

COPY ./service/requirements.txt /service/requirements.txt
RUN pip install -r /service/requirements.txt
COPY ./service /service

EXPOSE 5000

CMD ["python3", "-u", "./service/service.py"]
