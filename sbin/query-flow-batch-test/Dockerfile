# sbilife/query-flow-batch-test
FROM python:3.14-alpine

WORKDIR /usr/local/query-flow-batch-test

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    uuid==1.30 \
    python-dotenv==1.1.1 \
    reportlab==4.4.9 \
    pyyaml==6.0.2 \
    sbilifeco-http-client-query-flow==0.1.9

EXPOSE 80

ENV QUERY_FLOW_PROTO=http
ENV QUERY_FLOW_HOST=localhost
ENV QUERY_FLOW_PORT=80
ENV QUESTIONS_FILE=/var/lib/query-flow-batch-test/questions.yaml
ENV ANSWERS_FILE=/var/lib/query-flow-batch-test/answers.pdf
ENV DB_ID=nb

COPY envvars.py batch_test.py ./

ENTRYPOINT ["python", "batch_test.py"]