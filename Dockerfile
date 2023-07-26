FROM python:3.11

COPY ./blog /app
COPY ./requirements /requirements
COPY ./scripts /scripts
WORKDIR /app

RUN apt-get update -y && apt-get install python3-dev default-libmysqlclient-dev build-essential -y
RUN pip install -r /requirements/requirements.txt

CMD python manage.py run_local_server
