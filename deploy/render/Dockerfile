FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/matplotlib GIT_PYTHON_REFRESH=quiet
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock && useradd --uid 10001 --create-home appuser
COPY --chown=appuser:appuser . .
RUN mkdir -p /app/state /app/reports && chown -R appuser:appuser /app/state /app/reports
USER appuser
# Render supplies this build argument for the exact checked-out commit.
ARG RENDER_GIT_COMMIT
ENV GITHUB_SHA=${RENDER_GIT_COMMIT}
# Bake validated model state into this demo image. Render Free cannot retain
# runtime writes across restarts. Training gates must pass during the build.
RUN test -n "$GITHUB_SHA" && python -m capstone run
CMD ["sh", "-c", "exec python -m uvicorn capstone.api:create_app --factory --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
