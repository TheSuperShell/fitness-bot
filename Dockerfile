FROM python:3.12-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.2 /uv /uvx /bin/

WORKDIR /bot

COPY ./pyproject.toml .
COPY ./uv.lock .
COPY ./packages/ ./packages
COPY ./tools ./tools

ARG USE_WEBHOOK=false

RUN if [ ${USE_WEBHOOK} = true ]; then \
    uv sync --locked --no-dev --group webhook; else \
    uv sync --locked --no-dev; \
fi


FROM python:3.12-slim-trixie AS production

RUN useradd --create-home botuser
USER botuser

WORKDIR /bot

COPY --from=builder /bot/.venv .venv
COPY ./src ./src
COPY ./packages ./packages
COPY ./static ./static

ENV PATH="/bot/.venv/bin:$PATH"

CMD [ "python", "-m", "src.longpolling" ]