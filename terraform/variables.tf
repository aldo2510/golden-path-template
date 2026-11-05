variable "project_name" {
  description = "Short project identifier; lowercase letters, digits, and hyphens."
  type        = string
  default     = "goldenpathdemo"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9-]{2,19}$", var.project_name))
    error_message = "project_name must be 3-20 characters, begin with a letter, and contain only letters, digits, or hyphens."
  }
}

variable "location" {
  description = "Azure region for resources."
  type        = string
  default     = "eastus"
}

variable "azure_subscription_id" {
  description = "Azure subscription ID."
  type        = string
  sensitive   = true
}

variable "azure_deployer_object_id" {
  description = "Object ID of the service principal used by GitHub Actions."
  type        = string
}

variable "image_name" {
  description = "Full container image reference. A small public placeholder is used before the first build."
  type        = string
  default     = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
}

variable "container_cpu" {
  description = "CPU cores allocated to the container."
  type        = number
  default     = 0.25
}

variable "container_memory" {
  description = "Memory allocated to the container."
  type        = string
  default     = "0.5Gi"
}
