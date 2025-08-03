FROM node:24-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps
COPY frontend/ .
RUN npm run build

FROM python:3.13.3-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential pkg-config

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/

# RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
# ADD https://astral.sh/uv/install.sh /uv-installer.sh
# RUN sh /uv-installer.sh && rm /uv-installer.sh
# ENV PATH="/root/.local/bin/:$PATH"

COPY ./uv.lock .
COPY ./pyproject.toml .
RUN uv sync --locked

ADD . /app
RUN rm -rf frontend
COPY --from=frontend /frontend/assets ./frontend/assets

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8000
CMD [ "/entrypoint.sh" ]
