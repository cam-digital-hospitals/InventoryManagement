# Use a Python image compatible with the Raspberry Pi's architecture
FROM python:3.8

# Set environment variables to prevent Python from writing pyc files to disc
# and buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE="1"
ENV PYTHONUNBUFFERED="1"
ENV PYTHONPATH="/home/web/code"

# Create a user to avoid running containers as root in production
RUN addgroup --system web \
    && adduser --system --ingroup web web

# Install os-level dependencies (as root)
RUN apt-get update && apt-get install -y -q --no-install-recommends \
  # dependencies for building Python packages
  build-essential \
  # postgress client (psycopg2) dependencies
  # libpq-dev \
  # cleaning up unused files to reduce the image size
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Create a directory for the source code and use it as base path
WORKDIR /home/web/code/

# Copy the python depencencies list for pip
COPY ./requirements.txt requirements.txt

# Install python packages at system level
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . ./

# Set permissions and switch to 'web' user
RUN chmod -R u+w /home/web/code/ && chown -R web:web /home/web/code/
USER web

EXPOSE 8000
# CMD gunicorn inventory_project.wsgi:application --bind 0.0.0.0:8000