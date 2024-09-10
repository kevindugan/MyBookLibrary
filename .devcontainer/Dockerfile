FROM python:3.12-bookworm

RUN apt update && \
    apt install -y vim less jq yq git-lfs gnupg2 postgresql npm && \
    pip install -qU pip && \
    # Install python packages
    pip install fastapi uvicorn[standard] sqlalchemy psycopg2 pytest-cov pytest-postgresql httpx python-dotenv && \
    # Create container user
    useradd --shell /bin/bash --create-home book-api-user && \
    echo "\nexport PATH=/home/book-api-user/.local/bin:/opt/bin:\${PATH}" >> /home/book-api-user/.bashrc

USER book-api-user
