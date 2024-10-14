FROM python:3.12-slim

# cd to app directory
WORKDIR /app

# Install dependencies with cache
COPY requirements.txt /app/

# RUN python -m venv venv && \
#     ./venv/bin/pip install --upgrade pip && \
#     ./venv/bin/pip install -r requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the app
COPY . /app

# Setting up virtual environment
ENV PYTHONUNBUFFERED 1
# ENV VIRTUAL_ENV=/app/venv
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# ENV PATH="/app/venv/bin:$PATH"

CMD ["celery", "-A", "tgmonopoly", "worker", "-l", "INFO"]
# CMD ["ls", "/app"]
