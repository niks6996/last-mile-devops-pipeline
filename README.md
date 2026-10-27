# Last-Mile DevOps Portfolio: Stage 1

A fictional, read-only delivery tracking API built as a personal portfolio demonstration inspired by logistics. It contains sample data only and is not Petrocom's application or infrastructure.

## What works now

Python standard-library HTTP API, automated API tests, a non-root container image and a GitHub Actions workflow to run tests and build the image. No external packages are needed. The API stores two fixed example records in memory and is not a production service.

| GET endpoint | Purpose |
| --- | --- |
| `/healthz` | Liveness response |
| `/readyz` | Readiness response (no external dependencies yet) |
| `/deliveries` | List fictional deliveries |
| `/deliveries/DEL-1001` | Get one delivery; unknown IDs return 404 |

## Run locally (Python 3.12)

From this folder:

```powershell
python -m unittest discover -s tests -v
python -m app.server
```

In a second PowerShell window:

```powershell
Invoke-RestMethod http://localhost:8080/healthz
Invoke-RestMethod http://localhost:8080/deliveries
Invoke-RestMethod http://localhost:8080/deliveries/DEL-1001
```

Stop the server with Ctrl+C. Set `$env:PORT = "8081"` before starting it if port 8080 is occupied.

## Run with Docker

With Docker Desktop running:

```powershell
docker build -t last-mile-api:local .
docker run --rm -p 8080:8080 last-mile-api:local
```

Test with the same PowerShell requests above, then stop with Ctrl+C.

## Planned next stages

1. Add Kubernetes manifests with resource limits, health probes and a service.
2. Add image security scanning and publishing, then GitOps deployment and rollout/rollback tests.
3. Integrate with the existing EKS platform after reviewing its current configuration and cost implications.
4. Add application metrics, dashboards and tested alerts.

These are plans, not completed features. Do not claim zero downtime until it has been measured during a rollout. No AWS resources are created by this stage.
