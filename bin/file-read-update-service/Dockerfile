# sbilife/file-read-update-service
FROM python:3.12-slim

WORKDIR /usr/local/file-read-update-service

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    pydantic==2.11.9 \
    pyyaml==6.0.2 \
    sbilifeco-gateway-file-read-update==0.1.0 \
    sbilifeco-http-server-object-read-update==0.1.0

EXPOSE 80

ENV HTTP_PORT=80
ENV CONFIG_PATH=

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]