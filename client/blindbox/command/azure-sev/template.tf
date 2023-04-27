variable "image" {
  type        = string
  description = "The docker image tagged by `blindbox build`."
}

variable "cce_policy" {
  type        = string
  description = "The cce_policy generated by `blindbox build`."
}

# Configure the Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0.2"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }

  required_version = ">= 1.1.0"
}

# Azure Resource Management (azure-cli provider)
provider "azurerm" {
  features {}
}

# Local docker provider
provider "docker" {}

# Resource group
resource "azurerm_resource_group" "rg" {
  name     = "TestACIGroup"
  location = "North Europe"
}

resource "azurerm_container_registry" "acr" {
  name                = "amdSEVTestContainerRegistry284"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  # Allow admin credentials.
  admin_enabled = true
}

# Retag the image
resource "docker_tag" "image" {
  source_image = var.image
  target_image = "${azurerm_container_registry.acr.login_server}/${var.image}"
}

# Push the image
resource "null_resource" "docker_push" {
  provisioner "local-exec" {
    environment = {
      LOGIN_SERVER   = azurerm_container_registry.acr.login_server,
      ADMIN_USERNAME = azurerm_container_registry.acr.admin_username,
      ADMIN_PASSWORD = nonsensitive(azurerm_container_registry.acr.admin_password),
      IMAGE          = docker_tag.image.target_image
    }

    command = <<-EOT
      set -e
      docker login $LOGIN_SERVER \
          --username $ADMIN_USERNAME \
          --password $ADMIN_PASSWORD
      docker push $IMAGE
    EOT
  }
  depends_on = [
    docker_tag.image
  ]
}


# Container group
# We are using a template deployment (ARM file) since confidential-computing is not
#  supported by the azurerm terraform provider.
resource "azurerm_resource_group_template_deployment" "container" {
  name                = "blindbox"
  resource_group_name = azurerm_resource_group.rg.name

  template_content = jsonencode(
    {
      "$schema" : "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
      "contentVersion" : "1.0.0.1",
      "parameters" : {},
      "resources" : [
        {
          "type" : "Microsoft.ContainerInstance/containerGroups",
          "apiVersion" : "2022-10-01-preview",
          "name" : "blindbox",
          "location" : azurerm_resource_group.rg.location
          "properties" : {
            "confidentialComputeProperties" : {
              "ccePolicy" : var.cce_policy
            },
            "containers" : [
              {
                "name" : "blindbox",
                "properties" : {
                  "image" : docker_tag.image.target_image,
                  "ports" : [
                    {
                      "port" : 22,
                      "protocol" : "TCP"
                    }
                  ],
                  "resources" : {
                    "requests" : {
                      "cpu" : 1,
                      "memoryInGB" : 2
                    }
                  },
                }
              }
            ],
            "sku" : "Confidential",
            "osType" : "Linux",
            "restartPolicy" : "Always",
            "ipAddress" : {
              "type" : "Public",
              "ports" : [
                {
                  "port" : 22,
                  "protocol" : "TCP"
                }
              ]
            },
            "imageRegistryCredentials" : [
              {
                "server" : azurerm_container_registry.acr.login_server,
                "username" : azurerm_container_registry.acr.admin_username,
                "password" : azurerm_container_registry.acr.admin_password
              }
            ]
          }
        }
      ],
      "outputs" : {
        "containerIPv4Address" : {
          "type" : "string",
          "value" : "[reference(resourceId('Microsoft.ContainerInstance/containerGroups', 'blindbox')).ipAddress.ip]"
        }
      }
    }
  )

  depends_on = [
    null_resource.docker_push
  ]

  deployment_mode = "Incremental"
}

# output "container_ip" {
#   value = jsondecode(azurerm_resource_group_template_deployment.container.output_content).containerIPv4Address.value
# }

# output "cce_policy" {
#   value = data.local_file.cce_policy.content
# }

