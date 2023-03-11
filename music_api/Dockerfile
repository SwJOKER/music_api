FROM python:3.10.10-alpine

# set work directory
WORKDIR /usr/src/music_api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
# sed fix windows style line ending
RUN sed -i 's/\r$//g' /usr/src/music_api/entrypoint.sh
RUN chmod +x /usr/src/music_api/entrypoint.sh

# copy project
COPY . .

ENTRYPOINT ["/usr/src/music_api/entrypoint.sh"]