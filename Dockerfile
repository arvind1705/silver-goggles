# Notes
# -----
# 1. Uses a debian based system, not Alpine
# 1. Assumes application is configurable via environment variables,
#    and that there is a single settings.py file
# 1. Assumes Django based application. For Flask, you will delete the collectstatic command. 
#    Also, the wsgi application name in the ENTRYPOINT will also differ slightly.
# 1. This installs Postgres *AND* MySQL in separate steps. 
#    Delete either one or both depending on your use case
# 1. We create a user without any permissions, not even write permissions. This means you cannot 
#    write logs or create directories. You should write logs to stdout / stderr instead.
#

# This base image uses Debian operating system
FROM python:3.8-slim

# Create a user gunicorn so that we don't have to use root user
# We switch to gunicorn user at the bottom of this script
RUN groupadd --gid 1000 gunicorn \
  && useradd --uid 1000 --gid gunicorn --shell /bin/bash --create-home gunicorn

# This forces python to not buffer output / error
ENV PYTHONUNBUFFERED 1

# This is where we will copy all our code
# Workdir creates the directory if it doesn't exist
WORKDIR /code

# This installs libpq5, which is the postgres native driver
# This is needed later when we install psycopg2
RUN set -ex \
    && apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install psycopg2 before installing the other dependencies
# Psycopg2 requires installing dev packages, and is usually slower
# So we cache it in a separate layer
RUN set -ex \
    && BUILD_DEPS=" \
        build-essential \
        libpcre3-dev \
        libpq-dev \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && pip install --no-cache-dir 'psycopg2==2.8.3' \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------
# From here, the steps are application specific
# ---------------------------------------------
# Now copy requirements.txt and install all dependencies
# As a best practice, you should pin down version numbers in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining code
# Avoid copying the current working directory, 
# as that will have unnecessary files
# COPY manage.py .
# COPY periodic_task.py .

# COPY fampay fampay

COPY . .

# Generate static files
# Note that we pass a dummy secret key
# This secret key is not used when the server is actually started
RUN GOOGLE_DEVELOPER_KEY=ignore DB_NAME=ignore DB_USER=ignore DB_PASSWORD=ignore DB_HOST=ignore SECRET_KEY=ignore python manage.py collectstatic --noinput

# RUN python manage.py migrate

# Switch to gunicorn user
# This makes our container a lot more secure
USER gunicorn

