FROM nginx:latest

WORKDIR /var/www/html

RUN apt-get update

COPY nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]