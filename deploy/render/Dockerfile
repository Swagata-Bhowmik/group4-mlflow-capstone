# Public demo built from the exact image that passed the release workflow.
FROM swagata28/group4-mlflow-capstone@sha256:130e502e5228a531636db5fe3a307afcddb3d9605c3ac6b4f193756a69151675
ENV GITHUB_SHA=2be7c545c84cc8a1431f2eaf78d15fa1f5ac85e4
# Bake validated model state into this demo image. Render Free cannot retain
# runtime writes across restarts. Training gates must pass during the build.
RUN python -m capstone run
CMD ["sh", "-c", "exec python -m uvicorn capstone.api:create_app --factory --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
