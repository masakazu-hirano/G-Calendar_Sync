FROM python:3.11.5-slim-bookworm

RUN cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN apt-get update \
	&& apt-get install --yes --show-progress --verbose-versions cron vim git

RUN git config --global user.name mskzu-hirno \
	&& git config --global user.email @users.noreply.github.com \
	&& git config --global init.defaultBranch main

COPY . /usr/local/src
WORKDIR /usr/local/src

RUN pip install --upgrade pip \
	&& pip install --requirement requirements.txt
