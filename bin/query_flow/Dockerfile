# sbilife/query-flow
FROM python:3.12

WORKDIR /usr/local/query-flow

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    watchdog==6.0.0 \
    sbilifeco-models-base==0.1.3 \
    sbilifeco-models-db-metadata==0.1.6 \
    sbilifeco-http-client-llm==0.1.6 \
    sbilifeco-http-client-metadata-storage==0.1.5 \
    sbilifeco-http-client-session-data-manager==0.1.1 \
    sbilifeco-user-flow-generate-query==0.1.26 \
    sbilifeco-http-server-query-flow==0.1.16 \
    sbilifeco-cp-mcp-client==0.1.2

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
ENV PROMPTS_FILE=

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]
