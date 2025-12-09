# sbilife/redis-gateway
FROM python:3.12

WORKDIR /usr/local/redis-gateway

RUN pip install \
    --no-cache-dir \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-models-base==0.1.3 \
    sbilifeco-gateway-redis==0.1.2 \
    sbilifeco-http-server-session-data-manager==0.1.2 \
    sbilifeco-http-server-population-counter==0.1.0

EXPOSE 80 81

ENV HTTP_PORT_SESSION_DATA=80
ENV HTTP_PORT_POPULATION=81
ENV REDIS_HOST=localhost
ENV REDIS_PORT=6379
ENV REDIS_DB=0

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]

