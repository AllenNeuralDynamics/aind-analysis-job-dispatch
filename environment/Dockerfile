# hash:sha256:d5fb23188d806ae2d76ede381b4343b88bfe3b875d4ea460ae09c61316b0e74c
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/jupyterlab:3.6.1-miniconda4.12.0-python3.9-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive
ARG AWS_ACCESS_KEY_ID
ARG AWS_DEFAULT_REGION
ARG AWS_SECRET_ACCESS_KEY

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN pip install -U --no-cache-dir \
    aind-data-access-api[full]==1.0.0 \
    numpy==1.26.4 \
    pandas==2.1.4 \
    pydantic==2.10.6 \
    pydantic-settings==2.9.1 \
    s3fs==2025.2.0

COPY postInstall /
RUN /postInstall
