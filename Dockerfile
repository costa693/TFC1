# base image
FROM ubuntu:latest


# non interactive
ENV DEBIAN_FRONTEND noninteractive 

#\ TZ=Europe/Paris

# update packages
RUN apt-get update \
    && apt-get install -y apt-utils \
    && apt-get install -y wget

# install supporting software
RUN apt install software-properties-common -y \
    && add-apt-repository ppa:deadsnakes/ppa -y


# install python
RUN apt-get install python3.9 -y \
    && apt install python3.10-venv -y \
    && apt-get install python3-pip -y

# install opencv dependancies
RUN apt-get update
RUN apt-get install -y libsm6 libxext6 libxrender-dev
RUN apt-get install -y python3-opencv

# define the work directory
WORKDIR /usr/src/app

# create virtual env and activate env
RUN python3 -m venv venv

RUN . venv/bin/activate

# install requirements
COPY requirements.txt .

RUN python3 -m pip install --upgrade pip

# remove pkg_resources 0.0.0
RUN sed -i 's/pkg_resources==0.0.0//g' requirements.txt

# install ai-module
RUN python3 -m pip install -i https://test.pypi.org/simple/ yolo-realtime-congestion

# install other requirements
RUN python3 -m pip install -r requirements.txt


# copy sources
COPY . .

# freeze env
RUN python3 -m pip freeze > /usr/src/app/requirements.txt


# download Yolo packages
# RUN wget https://pjreddie.com/media/files/yolov3.weights -O ./.yolo/yolov3.weights

# expose app port
EXPOSE 8000

# entry point
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

# run
# docker build -t msft-learn-how-to-devops-django-app .