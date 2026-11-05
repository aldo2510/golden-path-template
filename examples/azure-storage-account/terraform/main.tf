terraform {
  required_version = ">= 1.6.0"
  backend "azurerm" {}
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

module "storage_account" {
  source = "git::https://github.com/aldo2510/platform-terraform-modules.git//modules/azure-storage-account?ref=main"

  subscription_id      = var.subscription_id
  resource_group_name  = var.resource_group_name
  storage_account_name = var.storage_account_name
  location             = var.location
  environment          = var.environment
  replication_type     = var.replication_type
}
