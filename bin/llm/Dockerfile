# sbilife/llm
FROM python:3.12

WORKDIR /usr/local/llm

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.0 \
    sbilifeco-cp-microservice-llm==0.1.0 \
    sbilifeco-gateways-gemini==0.1.0

EXPOSE 80

ENV HTTP_PORT=80
ENV LLM_MODEL=
ENV API_KEY=

COPY envvars.py service.py .

ENTRYPOINT ["python", "service.py"]
