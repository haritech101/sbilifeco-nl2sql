# sbilife/sqlalchemy-gateway
FROM python:3.14-alpine

WORKDIR /usr/local/sqlalchemy-gateway

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-gateway-sqlalchemy==0.1.0 \
    sbilifeco-http-server-metadata-storage==0.1.5

EXPOSE 80

ENV HTTP_PORT=80
ENV DEFINITIONS_PATH=

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]