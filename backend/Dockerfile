FROM python:3.8-alpine3.12
ENV PYTHONUNBUFFERED 1
WORKDIR /backend
ADD requirements.txt /backend/

COPY supervisord.conf /etc/supervisord.conf

RUN apk add --update --no-cache postgresql-client jpeg-dev supervisor nginx 
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev musl-dev python3-dev libffi-dev openssl-dev cargo
RUN pip install -r requirements.txt
RUN apk del .tmp-build-deps

ENV USER=app
ENV UID=12345
ENV GID=23456

RUN addgroup -S "${USER}" && adduser --disabled-password -S "${USER}" -G "${USER}" --no-create-home --uid "$UID" "$USER"
RUN chown -R "${USER}":"${USER}" /backend


ADD . /backend/
RUN chown -R "${USER}":"${USER}" /backend
COPY entrypoint.sh /backend/
RUN chmod +x entrypoint.sh

COPY celery.conf /etc/supervisor/conf.d/celery.conf
COPY supervisord.conf /etc/supervisord.conf

# Switch to app user
USER app
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]