# sbilife/answer-notify-flow
FROM python:3.14-slim

WORKDIR /usr/local/answer-notify-flow

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-flow-answer-notify==0.2.2 \
    sbilifeco-kafka-consumer-answer-notify-trigger==0.2.2 \
    sbilifeco-http-client-query-flow-answer-repo==0.2.2 \
    sbilifeco-presenter-html-query-flow-answers==0.1.5

EXPOSE 80

ENV KAFKA_URL=localhost:9092
ENV MAX_ITEMS=25
ENV ANSWER_REPO_PROTO=http
ENV ANSWER_REPO_HOST=localhost
ENV ANSWER_REPO_PORT=80
ENV WEB_PAGE_PATH=/var/lib/sbilifeco/analytics/query-flow-answers.html
ENV TEMPLATE_PATH=/var/lib/sbilifeco/templates/query-flow-answers-template.html

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]