# syntax=docker/dockerfile:1

FROM python:3.14-slim-trixie AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-compile -r requirements.txt


FROM python:3.14-slim-trixie AS runtime

ARG APP_UID=10001
ARG APP_GID=10001

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --system --gid ${APP_GID} contextbridge \
    && useradd --system --uid ${APP_UID} --gid contextbridge \
        --no-create-home contextbridge

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=contextbridge:contextbridge app ./app

USER contextbridge

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

