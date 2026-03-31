# haritech101/question-suggestion-flow
FROM python:alpine

WORKDIR /usr/local/question-suggestion-flow

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv>=1.1.1 \
    sbilifeco-flow-question-suggestion>=0.1.1 \
    sbilifeco-http-client-llm>=0.2.1 \
    sbilifeco-http-client-metadata-storage>=0.1.6 \
    sbilifeco-http-server-question-suggestion-flow>=0.1.1


EXPOSE 80

ENV HTTP_PORT=80
ENV METADATA_STORAGE_PROTO=http
ENV METADATA_STORAGE_HOST=localhost
ENV METADATA_STORAGE_PORT=80
ENV LLM_PROTO=http
ENV LLM_HOST=localhost
ENV LLM_PORT=80
ENV PROMPT_FILE=/var/lib/question-suggestion-flow/prompt.txt

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]