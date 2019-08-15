FROM python:3.7.3

RUN apt-get update
RUN apt install python3-pip build-essential libssl-dev libffi-dev python-dev --assume-yes

COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

RUN python3 --version

WORKDIR /app

COPY startup.sh /usr/local/startup.sh