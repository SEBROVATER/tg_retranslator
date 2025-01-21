FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD uv.lock /app/uv.lock
ADD pyproject.toml /app/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

# create directory for the nonroot user
RUN mkdir -p /home/nonroot

# create the nonroot user
#RUN addgroup --system nonroot && adduser --system --group nonroot

# create the nonrootrp opriate directories
ENV HOME=/home/nonroot
ENV APP_HOME=/home/nonroot/app
RUN mkdir -p ${APP_HOME}
WORKDIR ${APP_HOME}

# Copy the application from the builder
COPY --from=builder --chown=app:app /app ${APP_HOME}

# Place executables in the environment at the front of the path
ENV PATH="${APP_HOME}/.venv/bin:$PATH"

# copy project
COPY general_utils/ ${APP_HOME}/general_utils/
COPY main.py ${APP_HOME}


# chown all the files to the app user
#RUN chown -R nonroot:nonroot ${HOME}

# change to the nonroot user
#USER nonroot