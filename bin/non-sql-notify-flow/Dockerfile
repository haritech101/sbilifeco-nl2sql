# sbilife/non-sql-notify-flow
FROM python:3.14-slim

WORKDIR /usr/local/non-sql-notify-flow

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-flow-non-sql-notify==0.1.1 \
    sbilifeco-kafka-consumer-non-sql-notify-trigger==0.1.2 \
    sbilifeco-http-client-non-sql-answer-repo==0.1.0

EXPOSE 80

ENV KAFKA_URL=localhost:9092
ENV MAX_ITEMS=25
ENV NON_SQL_ANSWER_REPO_PROTO=http
ENV NON_SQL_ANSWER_REPO_HOST=localhost
ENV NON_SQL_ANSWER_REPO_PORT=80

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]