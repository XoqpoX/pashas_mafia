FROM python:3.10

WORKDIR /var/www/python

RUN pip install python-socketio

RUN pip install eventlet

EXPOSE 8000

CMD ["python", "main.py"] 