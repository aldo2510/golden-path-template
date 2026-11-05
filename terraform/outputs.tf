output "resource_group_name" {
  value = module.azure_container_apps.resource_group_name
}

output "acr_name" {
  value = module.azure_container_apps.acr_name
}

output "acr_login_server" {
  value = module.azure_container_apps.acr_login_server
}

output "container_app_name" {
  value = module.azure_container_apps.container_app_name
}

output "container_app_url" {
  value = module.azure_container_apps.container_app_url
}
