# sbilife/query-flow
FROM python:3.12

WORKDIR /usr/local/query-flow

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    sbilifeco-cp-http-client-llm==0.1.2 \
    sbilifeco-cp-http-client-metadata-storage==0.1.4 \
    sbilifeco-user-flows-query-flow==0.1.4 \
    sbilifeco-cp-microservice-query-flow==0.1.3 \
    python-dotenv==1.1.0

EXPOSE 80

ENV HTTP_PORT=80
ENV LLM_PROTO=http
ENV LLM_HOST=localhost
ENV LLM_PORT=80
ENV METADATA_STORAGE_PROTO=http
ENV METADATA_STORAGE_HOST=localhost
ENV METADATA_STORAGE_PORT=80

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]
