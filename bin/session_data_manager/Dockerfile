# sbilife/session-data-manager
FROM python:3.12

WORKDIR /usr/local/session-data-manager

RUN pip install \
    --no-cache-dir \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-gateway-redis==0.1.1 \
    sbilifeco-http-server-session-data-manager==0.1.2

EXPOSE 80

ENV HTTP_PORT=80
ENV REDIS_HOST=localhost
ENV REDIS_PORT=6379
ENV REDIS_DB=0

COPY envvars.py session_data_manager.py ./

ENTRYPOINT ["python", "session_data_manager.py"]

