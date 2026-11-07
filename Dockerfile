FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=8080
WORKDIR /app
COPY --chown=10001:10001 service.py .
USER 10001:10001

FROM base AS test
COPY --chown=10001:10001 test_service.py .
CMD ["python", "-m", "unittest", "-v", "test_service"]

FROM base AS runtime
ARG APP_VERSION=local
ENV APP_VERSION=${APP_VERSION}
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3)" || exit 1
CMD ["python", "service.py"]
