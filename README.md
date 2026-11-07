# Python Docker CI CD assignment

A small Python JSON service built and deployed with GitHub Actions. Azure Container Registry stores the tested image and Azure App Service runs it as a Linux Docker container.

## Service

- `/` returns a greeting and build version.
- `/health` returns `{"status": "ok"}`.
- `/version` returns the commit SHA of the deployed build.

There are no third-party Python dependencies. The standard-library HTTP server keeps this assignment small; production deployments would normally use a production web server.

## Pipeline

`.github/workflows/pipeline.yml` runs on pushes to main, pull requests and manual dispatch.

1. Build the Docker test target and run five HTTP tests.
2. Build the runtime image, run a container and check its health and commit version.
3. Save that tested image as a one-day workflow artifact.
4. On main, sign in to Azure through OpenID Connect, push the same image to ACR and deploy it to App Service.
5. Check the public endpoint for health and the expected commit version. An old healthy deployment does not count as success.

Pull requests do not deploy or receive an Azure identity. The deployment job remains skipped until Azure variables are configured; a green build alone is not evidence of cloud deployment.

## Local checks

```bash
python -m unittest -v test_service
python service.py
```

Or with Docker:

```bash
docker build --target test -t python-service-test .
docker run --rm python-service-test
docker build --target runtime --build-arg APP_VERSION=local -t python-service:local .
docker run --rm -p 8080:8080 python-service:local
```

## Azure connection

The Azure deployment template creates ACR Basic, a Linux B1 App Service plan, the web app, and a user-assigned managed identity for GitHub Actions. These Azure resources incur charges.

The identity trusts only `repo:gauravkumar2525/python-docker-cicd-assignment:ref:refs/heads/main`. It has Contributor on the assignment resource group and AcrPush on its registry. The web app has its own system-assigned identity with AcrPull. No Azure password, registry key or publish profile is committed.

Set these repository **Actions variables** after provisioning:

| Variable | Value |
|---|---|
| AZURE_CLIENT_ID | The GitHub deployment managed identity client ID |
| AZURE_TENANT_ID | Azure tenant ID |
| AZURE_SUBSCRIPTION_ID | Azure subscription ID |
| AZURE_RESOURCE_GROUP | Assignment resource group name |
| AZURE_ACR_NAME | Registry resource name |
| AZURE_WEBAPP_NAME | Web app name |

Then manually run the workflow, or push another commit to main.

## Evidence

Use an actual successful workflow run showing both jobs, the ACR image with the same commit SHA, and the running service response. A workflow with a skipped deployment is only a successful CI check.

After assessment, review and delete the dedicated Azure resource group if it is no longer needed. App Service and ACR continue to incur charges while provisioned.

## References

- [App Service containers and GitHub Actions](https://learn.microsoft.com/en-us/azure/app-service/deploy-container-github-action)
- [Azure OpenID Connect authentication](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect)
