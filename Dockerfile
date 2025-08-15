FROM docker:dind
RUN apk add --no-cache python3 ruff nodejs npm
RUN npm --version
COPY deploy /deploy