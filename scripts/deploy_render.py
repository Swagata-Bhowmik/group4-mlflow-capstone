"""Deploy the passing GitHub commit to Render; fail CI if deploy or lineage fails."""
import json
import os
import re
import time
import urllib.error
import urllib.request


def request_json(url, token=None, payload=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        # Do not include response bodies or request headers in CI logs.
        raise RuntimeError(f"HTTP {error.code} from {url}") from None


def main():
    token = os.environ.get("RENDER_API_KEY", "").strip()
    service = os.environ.get("RENDER_SERVICE_ID", "")
    # Rollbacks name an earlier released commit; normal releases deploy the workflow's own commit.
    commit = os.environ.get("DEPLOY_COMMIT") or os.environ.get("GITHUB_SHA", "")
    public_url = os.environ.get("CAPSTONE_PUBLIC_URL", "").rstrip("/")
    if not token or not re.fullmatch(r"srv-[a-z0-9]+", service):
        raise ValueError("Configure RENDER_API_KEY and RENDER_SERVICE_ID")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("GITHUB_SHA must be a full commit SHA")
    if not public_url.startswith("https://"):
        raise ValueError("CAPSTONE_PUBLIC_URL must use HTTPS")

    base = f"https://api.render.com/v1/services/{service}/deploys"
    deploy = request_json(base, token, {"commitId": commit, "clearCache": "do_not_clear"})
    deploy_id = deploy["id"]
    print(f"Render deploy {deploy_id}, commit {commit}", flush=True)
    deadline = time.monotonic() + 20 * 60
    previous_status = None
    while time.monotonic() < deadline:
        deploy = request_json(f"{base}/{deploy_id}", token)
        status = deploy["status"]
        if status != previous_status:
            print(f"Render status: {status}", flush=True)
            previous_status = status
        if status == "live":
            if deploy.get("commit", {}).get("id") != commit:
                raise RuntimeError("Render deployed a different commit")
            break
        if status in {"build_failed", "update_failed", "pre_deploy_failed", "canceled", "deactivated"}:
            raise RuntimeError(f"Render deployment ended with {status}")
        time.sleep(15)
    else:
        raise TimeoutError("Render did not finish within 20 minutes; check its dashboard")

    # Allow a short interval for the new instances to receive all public traffic.
    for attempt in range(12):
        try:
            health = request_json(public_url + "/health")
            lineage = request_json(public_url + "/lineage")
            if health.get("status") == "ok" and lineage.get("source", {}).get("commit") == commit:
                print(f"Verified healthy public API and model lineage for {commit}", flush=True)
                return
        except (RuntimeError, urllib.error.URLError, TimeoutError):
            pass
        time.sleep(10)
    raise RuntimeError("Public health/lineage does not match the deployed commit")


if __name__ == "__main__":
    main()
