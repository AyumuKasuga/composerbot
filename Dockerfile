FROM ubuntu:16.04

MAINTAINER AyumuKasuga

RUN locale-gen en_US.UTF-8

ENV LANG en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_ALL en_US.UTF-8

ENV TZ=Europe/Moscow

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get upgrade -y && apt-get install python3 python3-venv -y

RUN mkdir /composerbot

WORKDIR /composerbot

COPY *.py /composerbot/
COPY requirements.txt /composerbot/

RUN /usr/bin/python3 -m venv /composerbot/.venv
RUN chmod +x /composerbot/.venv/bin/activate
RUN cd /composerbot && /composerbot/.venv/bin/pip install pip --upgrade && /composerbot/.venv/bin/pip install -r requirements.txt

CMD /composerbot/.venv/bin/python -u bot.py