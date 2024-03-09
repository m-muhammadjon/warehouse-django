# pull official base image
FROM python:3.9.2-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1


# install psycopg2 dependencies
RUN apk update \
    && apk add libffi-dev  postgresql-dev wkhtmltopdf gcc python3-dev musl-dev py-pip jpeg-dev zlib-dev \
    && apk add libressl-dev perl rust libmagic pango openjpeg-dev g++ freetype-dev
RUN apk --no-cache add \
    icu-dev \
    gettext \
    gettext-dev

# Install font packages
RUN apk --no-cache add ttf-dejavu ttf-droid ttf-freefont ttf-liberation ttf-ubuntu-font-family

RUN apk update \
    && apk add --no-cache git \
       cmake \
       libstdc++ libgcc g++ \
       make \
       jpeg jpeg-dev \
       libpng libpng-dev \
       giflib giflib-dev \
       openblas \
       openblas-dev \
       ca-certificates curl wget \
    && rm -rf /var/cache/apk/*


COPY requirements/production.txt production.txt
COPY requirements/base.txt base.txt

COPY requirements/ .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r production.txt

# copy project
COPY . .


# copy entrypoint.sh
# COPY ./entrypoint.sh .

# copy project
#COPY . .

# run entrypoint.sh
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# create directory for the app user
RUN mkdir -p /home/app

# create the app user

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media
RUN mkdir $APP_HOME/locale
WORKDIR $APP_HOME

# copy entrypoint.sh
COPY ./entrypoint.sh $APP_HOME

# copy project
COPY . $APP_HOME

# VOLUME
#VOLUME /home/app/web/media


# chown all the files to the app user
# change to the app user

# run entrypoint.prod.sh
RUN ["chmod", "+x", "/home/app/web/entrypoint.sh"]
ENTRYPOINT ["/home/app/web/entrypoint.sh"]
