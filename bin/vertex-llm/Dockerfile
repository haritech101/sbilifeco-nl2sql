# sbilifeco/vertex-llm
# 
FROM python:3.12

WORKDIR /usr/local/vertex-llm

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    anthropic[vertex] \
    python-dotenv==1.1.1 \
    sbilifeco-gateway-vertex==0.1.0 \
    sbilifeco-http-server-llm==0.1.6

EXPOSE 80

ENV HTTP_PORT=80
ENV VERTEX_AI_REGION=us-central1
ENV VERTEX_AI_PROJECT_ID=prj-uat-di-genai
ENV VERTEX_AI_MODEL=claude-sonnet-4
ENV GOOGLE_APPLICATION_CREDENTIALS=

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]