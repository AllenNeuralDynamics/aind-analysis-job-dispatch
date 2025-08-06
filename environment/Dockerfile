# hash:sha256:b0f223ecc188cec5ea2a1d48edf6e2023ae0fd3caea01378f41cdb6bd69bad6a
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG AWS_ACCESS_KEY_ID
ARG AWS_DEFAULT_REGION
ARG AWS_SECRET_ACCESS_KEY

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN pip install -U --no-cache-dir \
    numpy==1.26.4 \
    pandas==2.1.4 \
    pydantic-settings==2.9.1 \
    s3fs==2025.2.0 \
    -e git+https://github.com/AllenNeuralDynamics/analysis-pipeline-utils@8a69491c67b79e5dcfb84084513ecba33b0160ed#egg=analysis-pipeline-utils

COPY postInstall /
RUN /postInstall
