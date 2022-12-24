FROM ubuntu:latest

RUN apt-get update; apt-get install -y python3 python3-pip
ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

ADD server /opt/server

EXPOSE 5000

CMD ["python3", "/opt/server/greeting_server.py"]
