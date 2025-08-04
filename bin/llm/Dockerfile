# sbilife/llm
FROM python:3.12

WORKDIR /usr/local/llm

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.0 \
    sbilifeco-microservice-llm==0.1.4 \
    sbilifeco-gateway-gemini==0.1.8

EXPOSE 80

ENV HTTP_PORT=80
ENV LLM_MODEL=
ENV API_KEY=
ENV PREAMBLE_FILE=
ENV POSTAMBLE_FILE=

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]
