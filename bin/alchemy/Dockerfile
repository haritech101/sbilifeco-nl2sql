# sbilife/alchemy
FROM python:3.12

WORKDIR /usr/local/<app>

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-mcp-server-sql-db==0.1.0 \
    sbilifeco-gateway-alchemy==0.1.1 \
    psycopg>=3.2.9

EXPOSE 80

ENV HTTP_PORT=80
ENV CONNECTION_STRING=sqlite:///./.local/alchemy.db
ENV SERVER_NAME="Relational Database Server"
ENV SERVER_INSTRUCTIONS="This MCP server points to a relational database. It will be used to access the database, mainly to run SQL queries"

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]