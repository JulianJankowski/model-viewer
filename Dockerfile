# syntax=docker/dockerfile:1
FROM python:3.8

RUN python3 -m pip install flask
RUN mkdir /app
WORKDIR /app
COPY . /app
ENV FLASK_APP=app.py
ENV PYTHONPATH /app
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]