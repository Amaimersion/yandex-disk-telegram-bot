FROM amaimersion/yd-tg-bot-app

# we will use "root" user for supervisor,
# but supervisor will spawn child processes
# under "yd-tg-bot" user
USER root

RUN \
    apt-get -yqq update && \
    apt-get -yqq install supervisor=3.3.5-1

CMD \
    supervisord \
    --configuration /etc/supervisor/supervisord.conf \
    --user root \
    --nodaemon
