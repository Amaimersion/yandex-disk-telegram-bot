FROM python:3.8.11

RUN adduser --disabled-password --gecos "" yd-tg-bot
ENV PATH="/home/yd-tg-bot/.local/bin:/home/yd-tg-bot/bin:$PATH"
WORKDIR /home/yd-tg-bot/app
RUN chown yd-tg-bot /home/yd-tg-bot/app
USER yd-tg-bot

COPY --chown=yd-tg-bot requirements.txt setup.py ./
RUN pip install --no-cache-dir -r requirements.txt

ENV \
    FLASK_ENV=production \
    CONFIG_NAME=production \
    GUNICORN_USE_IP_SOCKET=True \
    GUNICORN_PORT=8080

EXPOSE 8080

COPY --chown=yd-tg-bot translations translations
RUN pybabel compile -d ./translations --statistics

COPY --chown=yd-tg-bot migrations migrations

COPY --chown=yd-tg-bot scripts scripts
RUN chmod +x ./scripts/docker/app/run.sh

COPY --chown=yd-tg-bot wsgi.py manage.py babel.cfg ./
COPY --chown=yd-tg-bot src src

CMD ./scripts/docker/app/run.sh
