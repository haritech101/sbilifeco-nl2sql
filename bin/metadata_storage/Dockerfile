# sbilife/metadata-storage
FROM python:3.12

WORKDIR /usr/local/metadata-storage

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.0 \
    sbilifeco-gateways-fs-metadata-storage==0.1.4 \
    sbilifeco-cp-microservice-metadata-storage==0.1.4

EXPOSE 80

ENV HTTP_PORT=80
ENV METADATA_PATH=/var/lib/sbilifeco/db-metadata

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"] 

