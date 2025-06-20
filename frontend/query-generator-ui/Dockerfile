# sbilife/query-generator-ui
FROM node:22.16

WORKDIR /usr/local/query-generator-ui
COPY package*.json ./
RUN npm install
COPY *.ts *.json *.js *.html ./
COPY src ./src/
COPY public ./public/
ENV VITE_METADATA_URL=http://localhost
ENV VITE_QUERY_FLOW_URL=http://localhost
EXPOSE 80
ENTRYPOINT [ "npm", "run", "dev"]