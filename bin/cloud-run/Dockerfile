# gcr.io/prj-uat-di-website-agent/reverse-proxy-nl2sql
FROM nginx:alpine

COPY ./nl2sql.conf /etc/nginx/conf.d/default.conf.template

CMD ["/bin/sh", "-c", "envsubst '$TARGET_HOST,$TARGET_PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"]