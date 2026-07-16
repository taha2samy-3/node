ARG BASE_IMAGE=cgr.dev/chainguard/wolfi-base:latest
ARG PYTHON_VERSION=3.12
ARG PYTHON_FULL_VERSION

# ==========================================
# Stage 1: Development Image (full-dev)
# ==========================================
FROM ${BASE_IMAGE} AS full-dev

ARG PYTHON_VERSION
ARG PYTHON_FULL_VERSION

USER root

# Install full Python, pip, build tools, and tini
RUN apk update && apk add --no-cache \
    python-${PYTHON_VERSION}=${PYTHON_FULL_VERSION} \
    py${PYTHON_VERSION}-pip \
    build-base \
    tini

# Create non-root user, setup app dir, and create symlinks
RUN adduser -D -u 1000 python && \
    mkdir /app && chown python:python /app && \
    ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python && \
    ln -sf /usr/bin/pip${PYTHON_VERSION} /usr/bin/pip

WORKDIR /app
USER python

# Python specific environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Inline Entrypoint directly in Dockerfile
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python"]


# ==========================================
# Stage 2: Minimal Production Prep
# ==========================================
FROM ${BASE_IMAGE} AS minimal-prep

ARG PYTHON_VERSION
ARG PYTHON_FULL_VERSION

USER root

# Install ONLY the base python runtime and tini (No pip, no build tools)
RUN apk update && apk add --no-cache \
    python-${PYTHON_VERSION}-base=${PYTHON_FULL_VERSION} \
    tini

RUN adduser -D -u 1000 python && \
    mkdir /app && chown python:python /app && \
    ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python

# ==========================================
# Stage 3: Minimal Cleaner
# ==========================================
FROM minimal-prep AS minimal-cleaner

# Remove package manager and caches to shrink image size
RUN rm -rf \
    /lib/apk/db \
    /var/cache/apk \
    /etc/apk \
    /usr/share/apk \
    /usr/share/man \
    /usr/share/doc \
    /tmp/*

# ==========================================
# Stage 4: Final Production Image (minimal)
# ==========================================
FROM scratch AS minimal

# Copy the cleaned system
COPY --from=minimal-cleaner / /

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
USER python

# Inline Entrypoint directly in Dockerfile
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python"]