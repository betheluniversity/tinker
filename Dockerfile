FROM python:3.6 AS base

LABEL org.opencontainers.image.source="https://github.com/betheluniversity/tinker"

RUN mkdir -p /root/secrets && chmod 700 /root/secrets
RUN mkdir -p /srv/flask_app

EXPOSE 5000

RUN apt-get clean && \
    apt-get update -y && \
    apt-get install -y wget unzip ldap-utils libaio1 libldap2-dev libsasl2-dev net-tools

RUN pip install --upgrade pip

# Install requirements
COPY ./requirements.txt /srv/requirements.txt
RUN pip install -r /srv/requirements.txt --src /usr/local/src

# Create a start script that allows custom init scripts to run before the main command
RUN mkdir -p /entrypoint-init.d
COPY <<-"START_SCRIPT" /srv/entrypoint.sh
#!/bin/sh

# Run any scripts in /entrypoint-init.d
for script in /entrypoint-init.d/*; do
    if [ -f "$script" ]; then
        sh "$script"
    fi
done

exec "$@"
START_SCRIPT

WORKDIR /srv/flask_app

RUN chmod +x /srv/entrypoint.sh
ENTRYPOINT [ "/srv/entrypoint.sh" ]

FROM base AS debug
# Debug image reusing the base
# Install dev dependencies for debugging
RUN pip install debugpy
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

EXPOSE 5678

ENV FLASK_APP=tinker:app
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYDEVD_DISABLE_FILE_VALIDATION=1

CMD [ "sh", "-c", "python -m debugpy --listen 0.0.0.0:5678 -m flask run -h 0.0.0.0 -p 5000" ]

FROM base AS prod
# Production image
RUN pip install gunicorn

COPY . .
CMD [ "sh", "-c", "gunicorn --reload --bind 0.0.0.0:5000 'tinker:app' --access-logfile -" ]
