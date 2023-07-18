FROM python:3.11

COPY ./blog /app/blog
COPY ./requirements /app/requirements
COPY ./manage.py /app/manage.py
COPY ./.env /app/.env
WORKDIR /app

RUN apt-get update -y && apt-get install python3-dev default-libmysqlclient-dev build-essential -y
RUN pip install -r ./requirements/requirements.txt

CMD python manage.py run_local_server
