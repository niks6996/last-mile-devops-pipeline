FROM python:3.12-slim
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --no-create-home app
COPY app/ ./app/
USER app
EXPOSE 8080
CMD ["python", "-m", "app.server"]
