# hash:sha256:c80a7fbee3c2831d193d3df9c08fe6571e204969962499e6a2d16617336fdf43
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV DOCDB_HOST=api.allenneuraldynamics.org
ENV CODEOCEAN_DOMAIN=codeocean.allenneuraldynamics.org

RUN pip install -U --no-cache-dir \
    analysis-pipeline-utils==0.2.7 \
    boto3==1.42.30 \
    pydantic-settings==2.9.1 \
    s3fs==2026.1.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
