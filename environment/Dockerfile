# hash:sha256:c44c94036e33c9b5fc8348722f9b399224b73f9634369c2d7f110cb38f2e388d
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
    -e git+https://github.com/AllenNeuralDynamics/analysis-pipeline-utils@8722a08fc651ee0d4773927d91a5378ec8449980#egg=analysis-pipeline-utils
