# hash:sha256:5f66214248443e1b1e3caac26688cf87bab4cfaf68b0bbfa4049c25ba338f3d2
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG AWS_ACCESS_KEY_ID
ARG AWS_DEFAULT_REGION
ARG AWS_SECRET_ACCESS_KEY

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

ENV DOCDB_HOST=api.allenneuraldynamics-test.org
ENV DOCDB_DATABASE=analysis
ENV DOCDB_COLLECTION=processing_v2

RUN pip install -U --no-cache-dir \
    aind-data-access-api[docdb]==1.2.2 \
    numpy==1.26.4 \
    pandas==2.1.4 \
    pydantic-settings==2.9.1 \
    s3fs==2025.2.0

COPY postInstall /
RUN /postInstall
