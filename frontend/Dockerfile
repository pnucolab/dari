FROM node:24-alpine AS base

RUN apk upgrade --no-cache && apk add --no-cache bash

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable

WORKDIR /app

COPY package.json /app/
COPY pnpm-lock.yaml /app/
COPY pnpm-workspace.yaml /app/
RUN pnpm install

COPY . /app/
RUN pnpm run build

CMD ["bash", "run_server.sh"]
