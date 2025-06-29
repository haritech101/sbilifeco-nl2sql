# sbilife/metadata-manager
FROM node:22.16

WORKDIR /usr/local/metadata-manager
COPY package*.json ./
RUN npm install
COPY *.ts *.json *.js *.html ./
COPY src ./src/
COPY public ./public/
ENV VITE_API_PROTO=http
ENV VITE_API_HOST=localhost
ENV VITE_API_PORT=80
EXPOSE 80
ENTRYPOINT [ "npm", "run", "dev"]