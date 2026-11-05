# Golden Path: GitHub Actions + Terraform + Azure

Plantilla educativa para desplegar una aplicación Flask en Azure Container Apps usando GitHub Actions y Terraform.

## Qué crea

- Resource Group
- Azure Container Registry (ACR)
- Log Analytics Workspace
- Container Apps Environment
- Azure Container App
- Identidad administrada para que Container App descargue imágenes desde ACR

El pipeline crea primero la infraestructura base, construye y publica la imagen en ACR, y luego actualiza la Container App con la imagen recién creada.

## Requisitos

1. Una suscripción de Azure con permisos para crear recursos y asignaciones RBAC.
2. Un Service Principal de Azure (client ID, client secret, tenant ID y subscription ID).
3. GitHub Actions habilitado en el repositorio.

## 1. Configura GitHub Actions

En **Settings → Secrets and variables → Actions**, crea estos **secrets**:

- `AZURE_CLIENT_ID`: Application (client) ID del Service Principal.
- `AZURE_CLIENT_SECRET`: secreto del Service Principal.
- `AZURE_TENANT_ID`: Tenant ID.
- `AZURE_SUBSCRIPTION_ID`: Subscription ID.

Crea estas **variables** (no son secretos):

- `TF_PROJECT_NAME`: nombre corto del proyecto, solo letras, números y guiones; debe comenzar por letra, por ejemplo `goldenpathdemo`.
- `AZURE_PRINCIPAL_OBJECT_ID`: Object ID del **service principal enterprise application** (no el Application/Client ID). Se usa para conceder permisos de escritura en ACR.

El principal necesita permisos suficientes para desplegar los recursos del ejemplo y crear asignaciones de roles. En un entorno real, aplica mínimo privilegio y no otorgues Owner por comodidad.

## 2. Preparar la autenticación

Este taller usa `azure/login@v2` con Service Principal + Client Secret, no OIDC. No agregues credenciales al repositorio ni a archivos `.tfvars`. Rota y elimina el secreto al terminar el taller. Para producción, prefiere federación de identidad (OIDC) cuando sea posible.

## 3. Desplegar

Haz push a `main` (o ejecuta manualmente el workflow **Deploy Golden Path** desde Actions). El pipeline:

1. Inicia sesión en Azure.
2. Ejecuta `terraform apply` para aprovisionar la base.
3. Construye la imagen en ACR mediante `az acr build`.
4. Ejecuta Terraform de nuevo para configurar la imagen de la aplicación.
5. Imprime la URL pública de la aplicación.

El primer aprovisionamiento puede tardar varios minutos; no todo el flujo terminará en segundos.

## 4. Destruir los recursos

Ejecuta manualmente **Destroy Golden Path** desde Actions. El workflow pide confirmar el nombre del proyecto antes de ejecutar `terraform destroy`. La destrucción elimina los recursos creados por el taller; verifica antes de usarlo con recursos reales.

## Estructura

```text
.
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── terraform/
│   ├── versions.tf
│   ├── variables.tf
│   ├── main.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
└── .github/workflows/
    ├── deploy.yml
    └── destroy.yml
```

## Notas del taller

- Terraform state se guarda en el workspace del runner, por lo que esta versión es apropiada para una demostración de una sola ejecución controlada, no para trabajo en equipo ni para ejecuciones concurrentes. Para un entorno compartido, configura un backend remoto de Azure Storage con acceso y bloqueo adecuados.
- El ejemplo utiliza `az acr build`, así que no necesita Docker instalado en el runner.
- Revisa los costos y elimina los recursos al finalizar.
