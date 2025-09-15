# sbilife/query-flow
FROM python:3.12

WORKDIR /usr/local/query-flow

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    sbilifeco-models-base==0.1.3 \
    sbilifeco-http-client-llm==0.1.6 \
    sbilifeco-http-client-metadata-storage==0.1.5 \
    sbilifeco-http-client-session-data-manager==0.1.1 \
    sbilifeco-user-flow-generate-query==0.1.22 \
    sbilifeco-http-server-query-flow==0.1.13 \
    python-dotenv==1.1.0

EXPOSE 80

ENV HTTP_PORT=80
ENV LLM_PROTO=http
ENV LLM_HOST=localhost
ENV LLM_PORT=80
ENV METADATA_STORAGE_PROTO=http
ENV METADATA_STORAGE_HOST=localhost
ENV METADATA_STORAGE_PORT=80
ENV SESSION_DATA_PROTO=http
ENV SESSION_DATA_HOST=localhost
ENV SESSION_DATA_PORT=80
ENV PREAMBLE_FILE=
ENV POSTAMBLE_FILE=

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]
