FROM python:3.11-slim

# Set environment variables
# Set PYTHONUNBUFFERED=1 to ensure logs are output immediately.
# Set PIP_NO_CACHE_DIR=1 to prevent caching, reducing image size.
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# set the  working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-traditional
COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

RUN chmod +x /code/entrypoint.sh
ENTRYPOINT ["/code/entrypoint.sh"]