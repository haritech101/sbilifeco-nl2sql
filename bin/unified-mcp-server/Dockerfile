# sbilife/unified-mcp-server
FROM python:3.14-alpine

WORKDIR /usr/local/unified-mcp-server

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-mcp-server-unified==0.1.0 \
    sbilifeco-http-client-population-counter==0.1.0

EXPOSE 80

ENV HTTP_PORT=80
ENV POPULATION_COUNTER_PROTO=http
ENV POPULATION_COUNTER_HOST=localhost
ENV POPULATION_COUNTER_PORT=80

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]