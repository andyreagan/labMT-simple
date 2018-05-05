FROM ubuntu:14.04

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y --force-yes install make unzip g++ libssl-dev git xvfb x11-xkb-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic x11-apps clang libdbus-1-dev libgtk2.0-dev libnotify-dev libgnome-keyring-dev libgconf2-dev libasound2-dev libcap-dev libcups2-dev libxtst-dev libxss1 libnss3-dev gcc-multilib g++-multilib
RUN apt-get install -y curl
# RUN apt-get install -y nodejs
# RUN apt-set install npm
RUN curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
RUN apt-get install -y nodejs
# RUN sudo apt-get install -y build-essential
# RUN sudo apt-get install -y npm
RUN npm install electron-prebuilt
RUN npm install electron-html-to

COPY * /home/
