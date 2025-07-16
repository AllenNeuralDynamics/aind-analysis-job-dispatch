# hash:sha256:a0bfd59bde6d5483099f4b746a48442566ba0b693ef960604686217a5df68b07
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
    -e git+https://github.com/AllenNeuralDynamics/analysis-pipeline-utils@ee8b95b18da98e96d2778b223cb05e41b9b65554#egg=aind-analysis-results
