FROM python:3.7.3

RUN apt-get update
RUN apt install python-pip build-essential libssl-dev libffi-dev python-dev --assume-yes --fix-missing

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN python3 --version

WORKDIR /app

COPY startup.sh /usr/local/startup.sh