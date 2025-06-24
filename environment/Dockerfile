# hash:sha256:3cb5e058254349358cd5429be2bddb92ca57175ac66b5ed86c4628108133a50e
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
    numpy==1.26.4 \
    pandas==2.1.4 \
    pydantic-settings==2.9.1 \
    s3fs==2025.2.0 \
    -e git+https://github.com/AllenNeuralDynamics/aind-analysis-results.git@c64c0526d3b6ed4b8a1aa9334698a810b560607d#egg=aind-analysis-results

COPY postInstall /
RUN /postInstall
