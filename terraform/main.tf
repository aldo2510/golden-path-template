module "azure_container_apps" {
  source = "git::https://github.com/aldo2510/platform-terraform-modules.git//modules/azure-container-apps?ref=main"

  project_name             = var.project_name
  location                 = var.location
  azure_deployer_object_id = var.azure_deployer_object_id
  image_name               = var.image_name
}
