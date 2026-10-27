FROM python:3.12-slim

WORKDIR /app

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 --no-create-home app

COPY app/ ./app/

USER 10001:10001

EXPOSE 8080

CMD ["python", "-m", "app.server"]