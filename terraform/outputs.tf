output "resource_group_name" {
  description = "Resource group created for the demo."
  value       = azurerm_resource_group.main.name
}

output "acr_name" {
  description = "Azure Container Registry name."
  value       = azurerm_container_registry.main.name
}

output "acr_login_server" {
  description = "Azure Container Registry login server."
  value       = azurerm_container_registry.main.login_server
}

output "container_app_name" {
  description = "Azure Container App name."
  value       = azurerm_container_app.main.name
}

output "container_app_url" {
  description = "Public URL of the application."
  value       = "https://${azurerm_container_app.main.latest_revision_fqdn}"
}
