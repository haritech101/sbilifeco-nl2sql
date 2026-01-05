# sbilife/config-editor-ui
FROM node:lts-alpine

RUN npm install -g serve
EXPOSE 80
WORKDIR /app
ENV HTTP_PORT=80
ENV API_URL=http://localhost

COPY editor-ui/index.html ./editor-ui/index.html
COPY editor-ui/pages ./editor-ui/pages/
COPY editor-ui/css ./editor-ui/css/
COPY editor-ui/scripts/*.js ./editor-ui/scripts/
COPY start.sh ./

ENTRYPOINT [ "sh", "start.sh" ]