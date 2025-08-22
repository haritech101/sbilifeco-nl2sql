# sbilife/metadata-storage
FROM python:3.12

WORKDIR /usr/local/metadata-storage

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.0 \
    sbilifeco-models-base==0.1.3 \
    sbilifeco-gateway-synmetrix==0.1.4 \
    sbilifeco-http-server-metadata-storage==0.1.5

EXPOSE 80

ENV MICROSERVICE_PORT=80

ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_USERNAME=
ENV DB_PASSWORD=
ENV DB_NAME=

ENV AUTH_PROTO=http
ENV AUTH_HOST=localhost
ENV AUTH_PORT=80
ENV AUTH_USERNAME=
ENV AUTH_PASSWORD=
ENV AUTH_PATH=/auth

ENV CUBE_PORT=80

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"] 
