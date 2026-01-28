# sbilife/kafka-as-repo
FROM python:3.12-slim

WORKDIR /usr/local/kafka-as-repo

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-http-server-non-sql-answer-repo==0.1.0 \
    sbilifeco-gateway-kafka-as-repo==0.1.0

EXPOSE 80

ENV HTTP_PORT=80
ENV KAFKA_URL=localhost:9092
ENV KAFKA_CONSUMER_NAME=non-sql-answer-consumer
ENV ANSWER_TIMEOUT=5

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]