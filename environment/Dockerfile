# hash:sha256:39c6508f6266aca02b9394b34705005582e00bd0b02ddb645f53222837f9bb60
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-askpass /

RUN --mount=type=secret,id=git-access-token \
    GIT_ACCESS_TOKEN="$(cat /run/secrets/git-access-token)" \
    pip install -U --no-cache-dir \
    boto3==1.42.30 \
    pydantic-settings==2.9.1 \
    s3fs==2026.1.0 \
    -e git+https://github.com/AllenNeuralDynamics/analysis-pipeline-utils@db4f879249e50338529aab830b26d94eeff9911e#egg=analysis-pipeline-utils

COPY postInstall /
RUN --mount=type=secret,id=secrets . /run/secrets/secrets \
    && /postInstall
