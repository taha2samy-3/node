ARG NODE_VERSION=22

FROM cgr.dev/chainguard/wolfi-base AS full-dev

ARG NODE_VERSION

USER root

RUN apk update && apk add --no-cache \
    nodejs-${NODE_VERSION} \
    npm

RUN adduser -D -u 1000 node && \
    mkdir /app && chown node:node /app

COPY docker-entrypoint.sh /usr/bin/docker-entrypoint.sh
RUN chmod +x /usr/bin/docker-entrypoint.sh

WORKDIR /app
USER node

ENTRYPOINT ["/usr/bin/docker-entrypoint.sh"]
CMD ["node"]

FROM cgr.dev/chainguard/wolfi-base AS minimal-prep

ARG NODE_VERSION

USER root

RUN apk update && apk add --no-cache \
    nodejs-${NODE_VERSION}-minimal-compat \
    tini

RUN adduser -D -u 1000 node && \
    mkdir /app && chown node:node /app

COPY docker-entrypoint.sh /usr/bin/docker-entrypoint.sh
RUN chmod +x /usr/bin/docker-entrypoint.sh

FROM minimal-prep AS minimal-cleaner

RUN rm -rf \
    /lib/apk/db \
    /var/cache/apk \
    /etc/apk \
    /usr/share/apk \
    /usr/share/man \
    /usr/share/doc \
    /tmp/*

FROM scratch AS minimal

COPY --from=minimal-cleaner / /

ENV NODE_ENV=production
WORKDIR /app
USER node

ENTRYPOINT ["/sbin/tini", "--", "/usr/bin/docker-entrypoint.sh"]
CMD ["node"]