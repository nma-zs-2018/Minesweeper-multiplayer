FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
RUN apt-get update && apt-get install -y redis-server
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
CMD redis-server --daemonize yes && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000