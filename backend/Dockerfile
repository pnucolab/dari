FROM python:3.15-alpine

RUN apk upgrade --no-cache \
    && apk add --no-cache bash google-authenticator libqrencode-tools netcat-openbsd libldap libsasl

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN apk add --no-cache --virtual .build-deps build-base openldap-dev cyrus-sasl-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

COPY . /app

CMD ["bash", "scripts/start.sh"]
