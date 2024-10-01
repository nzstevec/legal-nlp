# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.11.9
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/crap" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY . .

RUN python -m pip install transformers==4.39.3 gliner==0.2.8 gliner-spacy==0.0.10 

RUN python -m pip install -U transformers "huggingface_hub[cli]"

WORKDIR /src/legal_nlp/frontend/components/streamlit-agraph
RUN python -m pip install .

# Install the package in editable mode
WORKDIR /src/legal_nlp
RUN mkdir -p /crap/.cache/huggingface/crap && \
    chmod -R 666 /crap/.cache/huggingface/crap && \
    chown -R appuser:appuser /crap && \
    chown appuser:appuser /src && \
    chown appuser:appuser /src/legal_nlp

# Install graphviz
RUN apt-get update && \
    apt-get install -y graphviz

# Switch to the non-privileged user to run the application.
USER appuser

# RUN huggingface-cli login --token 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

# Expose the port that the application listens on.
EXPOSE 8080 8501 8542 2234 2235

# Run the application.
# CMD ["./start_both.sh"]
# CMD ["streamlit","run","start_both.py","--server.headless","true","--server.port","8080"]
CMD ["python", "start_both.py"]
