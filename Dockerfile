FROM python:3.12-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.2 /uv /uvx /bin/

WORKDIR /bot

COPY ./pyproject.toml .
COPY ./uv.lock .
COPY ./packages/ ./packages

RUN uv sync --locked

FROM python:3.12-slim-trixie AS production

RUN useradd --create-home botuser
USER botuser

WORKDIR /bot

COPY --from=builder /bot/.venv .venv
COPY ./src ./src
COPY ./packages ./packages

ENV PATH="/bot/.venv/bin:$PATH"

CMD [ "python", "-m", "src.longpolling" ]