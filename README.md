# Golden Path Template — GitHub Actions + Terraform + Azure

This repository is the **application template**. Use GitHub's **Use this template** to create a new application repository. Each new app repository gets its own source code and invokes shared workflows and Terraform modules from separate platform repositories.

## Architecture

1. `golden-path-template` — application scaffold (Flask, Dockerfile, thin Terraform root module, workflow caller).
2. `platform-workflows` — reusable GitHub Actions workflows for deploy and destroy.
3. `platform-terraform-modules` — reusable Azure infrastructure module.
4. Azure — Resource Group, ACR, Log Analytics, Container Apps Environment, Container App.

A push to `main` in an app repo calls the shared deploy workflow. It initializes remote Terraform state, creates the infrastructure, builds `app/` using ACR Tasks, and updates the Container App to use the new image.

## Before running the workflow

### 1. Create remote Terraform state storage once

The workflow expects an existing Azure Storage account and blob container for Terraform state. Example commands (change the globally unique storage account name):

```bash
az login
az account set --subscription "<AZURE_SUBSCRIPTION_ID>"
az group create --name rg-goldenpath-tfstate --location eastus
az storage account create \
  --name stgoldenpathstate123 \
  --resource-group rg-goldenpath-tfstate \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2 \
  --allow-blob-public-access false
az storage container create \
  --name tfstate \
  --account-name stgoldenpathstate123 \
  --auth-mode login
```

Give the GitHub Actions Service Principal **Storage Blob Data Contributor** on the storage account (or the state container). This backend is shared across app repositories; the workflow uses a different state key per `TF_PROJECT_NAME`.

### 2. Add repository secrets

In **Settings → Secrets and variables → Actions → Secrets**, configure:

- `AZURE_CLIENT_ID`: Application (client) ID of the Azure Service Principal.
- `AZURE_CLIENT_SECRET`: its client secret.
- `AZURE_TENANT_ID`: Directory (tenant) ID.
- `AZURE_SUBSCRIPTION_ID`: subscription ID.

Authentication for this workshop is **Service Principal + Client Secret, not OIDC**. Never commit the secret or put it in a Terraform file.

### 3. Add repository variables

In **Settings → Secrets and variables → Actions → Variables**, configure:

- `TF_PROJECT_NAME`: unique short identifier, e.g. `clientesapi` (3–20 letters/digits/hyphens, begins with a letter).
- `AZURE_PRINCIPAL_OBJECT_ID`: Object ID of the Service Principal's Enterprise Application, not its Client ID.
- `AZURE_LOCATION`: optional Azure region, e.g. `eastus`.
- `TF_STATE_RESOURCE_GROUP`: e.g. `rg-goldenpath-tfstate`.
- `TF_STATE_STORAGE_ACCOUNT`: the actual storage account name.
- `TF_STATE_CONTAINER`: e.g. `tfstate`.

The Service Principal needs permission to create the required Azure resources and assign the ACR roles. For this workshop, arrange suitable resource-creation and role-assignment permissions before running. Scope permissions narrowly; do not automatically grant Owner in production.

## Run it

1. Use **Use this template** to create a new repository for your application.
2. Configure the four secrets and six variables above in the new repository.
3. Push a change to `main`, or manually run **Deploy Golden Path** from Actions.
4. Open the job summary to get the public application URL.
5. When finished, run **Destroy Golden Path** and type the exact project name to confirm.

The first deployment can take several minutes because Azure resources and a container image need to be provisioned. Azure resources and Log Analytics ingestion may incur charges. Destroy the app infrastructure after the workshop; the separately created Terraform state storage remains.

## Layout

```text
app/                              # App source and Dockerfile
terraform/                        # Thin root module, references shared module
.github/workflows/deploy.yml      # Calls platform-workflows
.github/workflows/destroy.yml     # Calls platform-workflows
```

## Notes

- Shared workflow and module references currently point to `main` to keep the classroom setup easy to follow. For a governed platform, pin both references to reviewed release tags or commit SHAs.
- This is a teaching starter, not a production platform baseline. Add tests, policy checks, release versioning, cost controls, observability, and environment approvals before broader use.
