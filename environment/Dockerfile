# hash:sha256:919241faba11a69777785da46857e2921f1560278d99e2797d95d229fb593925
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

ENV DOCDB_HOST=api.allenneuraldynamics.org
ENV CODEOCEAN_DOMAIN=codeocean.allenneuraldynamics.org

RUN pip install -U --no-cache-dir \
    analysis-pipeline-utils==0.2.8 \
    boto3==1.42.30 \
    pydantic-settings==2.9.1 \
    s3fs==2026.1.0

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
