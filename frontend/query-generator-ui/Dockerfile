# sbilife/query-generator-ui
FROM node:lts-alpine

WORKDIR /usr/local/query-generator-ui
EXPOSE 80
ENV VITE_APP_BASE_PATH=/query-ui
ENV VITE_METADATA_URL=http://localhost
ENV VITE_QUERY_FLOW_URL=http://localhost
ENV VITE_APP_PORT=80

COPY package*.json ./
RUN npm install

COPY *.ts *.json *.js *.html run.sh ./
COPY src ./src/
COPY public ./public/

ENTRYPOINT [ "sh", "run.sh" ]