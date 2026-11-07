# Python service with GitHub Actions and Docker

This assignment uses **GitHub Actions** as its only CI/CD tool. It builds a Python service into a Docker image, deploys the tested image to a fresh Docker host in a separate job, and verifies the running service.

## Files

```text
.github/workflows/pipeline.yml   CI/CD pipeline
service.py                       Python JSON HTTP service
test_service.py                  Five automated HTTP tests
smoke_test.py                    Health and build-version verification
Dockerfile                       Test and runtime image targets
.dockerignore
.gitignore
.gitattributes
```

## How it works

Push to main -> test -> build image -> save image artifact -> deploy container -> verify service -> save evidence.

The **Build and test Docker image** job runs the Python tests inside Docker, builds a runtime image tagged with the commit SHA, and smoke-tests it. It exports the exact tested image as a workflow artifact.

The **Deploy and run Docker service** job downloads that image on a different runner, loads it, and starts a detached container with port 8080 mapped. It verifies `/health` and checks `/version` matches the commit SHA. It also records the running container, endpoint responses and container logs as downloadable evidence. Failed checks fail the workflow. Pull requests run CI without deployment.

**Deployment scope:** this is a working demonstration deployment on a GitHub-hosted runner. The container is stopped after evidence is collected and the runner is discarded. It is not a permanent public website. A continuously running deployment would require a persistent Docker host; that is not set up in this assignment.

## Run the pipeline

The workflow runs automatically on a push to `main`, on a pull request targeting `main`, or manually from **Actions > Python Docker CI CD > Run workflow**. No Azure account, Docker Hub account, deployment secrets or paid cloud resources are required. GitHub-hosted runner usage and artifact storage are subject to your GitHub plan and quotas.

## Run locally

Python uses only the standard library; there are no pip dependencies.

```bash
python -m unittest -v test_service
python service.py
```

Open `http://localhost:8080/`, `/health` and `/version`.

With Docker:

```bash
docker build --target test -t python-service-test .
docker run --rm python-service-test
docker build --target runtime --build-arg APP_VERSION=local -t python-service:local .
docker run --rm -p 8080:8080 python-service:local
```

The image runs as an unprivileged user. Its Docker health check calls `/health`. The standard-library HTTP server keeps this example small; production services normally use a production web server.

## Submission evidence

In a successful workflow run, both jobs should be green. Download `deployment-evidence` to see the container listing, endpoint JSON and container logs. The `tested-docker-image` artifact contains the image tar and can be loaded using `docker load -i python-service.tar`. Artifacts are retained for seven days; download them before they expire.
