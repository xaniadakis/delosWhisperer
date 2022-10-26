# Dockerfile
FROM python:3.10-buster

# install nginx
RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# copy source and install dependencies
RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/pip_cache
RUN mkdir -p /opt/app/delosWhisperer
COPY requirements.txt start-server.sh /opt/app/
COPY .pip_cache /opt/app/pip_cache/
COPY delosWhisperer /opt/app/delosWhisperer/
WORKDIR /opt/app
RUN pip3 install -r requirements.txt --cache-dir /opt/app/pip_cache
RUN chown -R www-data:www-data /opt/app
RUN mkdir "/root/Videos"
RUN chmod 777 /root/Videos


# start server
EXPOSE 8000
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]