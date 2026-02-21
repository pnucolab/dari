FROM python:3.14-slim

RUN apt update && apt install -y libpam-google-authenticator qrencode libldap2-dev libsasl2-dev build-essential netcat-traditional && apt clean

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["bash", "scripts/start.sh"]