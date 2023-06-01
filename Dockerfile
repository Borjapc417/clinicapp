FROM python:3.8-alpine

RUN apk add --no-cache git postgresql-dev gcc libc-dev
RUN apk add --no-cache gcc g++ make libffi-dev python3-dev build-base

RUN pip install gunicorn
RUN pip install psycopg2
RUN pip install ipdb
RUN pip install ipython

WORKDIR /code/clinicapp

COPY . /code/clinicapp

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
