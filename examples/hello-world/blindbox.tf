# These are config values, feel free to change them how you want.
locals {
  resource_group_name     = "blindbox-test${random_integer.group_suffix.result}"
  location                = "North Europe"
  container_registry_name = "blindbox${random_integer.group_suffix.result}"

  # Resources
  cpu_count    = 1
  memory_in_gb = 15

  # Exposed ports to the outside world
  container_ports = [
    {
      port     = 80
      protocol = "TCP"
    },
  ]
}

resource "random_integer" "group_suffix" {
  min = 0
  max = 1000000
}

variable "image" {
  type        = string
  description = "The docker image tagged by `blindbox build`."
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
  name     = local.resource_group_name
  location = local.location
}

resource "azurerm_container_registry" "acr" {
  name                = local.container_registry_name
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
    docker_tag.image,
    azurerm_container_registry.acr,
  ]
  triggers = {
    image          = var.image,
    retag          = docker_tag.image.source_image_id,
    LOGIN_SERVER   = azurerm_container_registry.acr.login_server,
    ADMIN_USERNAME = azurerm_container_registry.acr.admin_username,
    ADMIN_PASSWORD = azurerm_container_registry.acr.admin_password,
    IMAGE          = docker_tag.image.target_image
  }
}

resource "null_resource" "make_cce_policy" {
  provisioner "local-exec" {
    environment = {
      DOCKER_IMAGE = docker_tag.image.target_image
    }

    # sed and tr will trim the thing
    command = <<-EOT
        az confcom acipolicygen --image "$DOCKER_IMAGE" \
            --print-policy \
            | sed -E 's/[^A-Za-z0-9+/=]//g' | tr -d '\n' \
            > "${path.module}/cce_policy.txt"
    EOT
  }

  depends_on = [
    null_resource.docker_push
  ]
  triggers = {
    image          = var.image,
    retag          = docker_tag.image.source_image_id,
    LOGIN_SERVER   = azurerm_container_registry.acr.login_server,
    ADMIN_USERNAME = azurerm_container_registry.acr.admin_username,
    ADMIN_PASSWORD = azurerm_container_registry.acr.admin_password,
    IMAGE          = docker_tag.image.target_image
  }
}

data "local_file" "cce_policy" {
  filename   = "${path.module}/cce_policy.txt"
  depends_on = [null_resource.make_cce_policy]
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
              "ccePolicy" : data.local_file.cce_policy.content
            },
            "containers" : [
              {
                "name" : "blindbox",
                "properties" : {
                  "image" : docker_tag.image.target_image,
                  "ports" : local.container_ports,
                  "resources" : {
                    "requests" : {
                      "cpu" : local.cpu_count,
                      "memoryInGB" : local.memory_in_gb
                    }
                  },
                  "securityContext": {
                      "privileged": true
                  }
                }
              }
            ],
            "sku" : "Confidential",
            "osType" : "Linux",
            "restartPolicy" : "Always",
            "ipAddress" : {
              "type" : "Public",
              "ports" : local.container_ports
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

# Get the resulting azure portal url
data "azurerm_client_config" "current" {}

locals {
  tenant_id   = data.azurerm_client_config.current.tenant_id
  portal_url  = "https://portal.azure.com"
  resource_id = azurerm_resource_group_template_deployment.container.id
}

output "cce_policy" {
  value = data.local_file.cce_policy.content
}

locals {
  arm_deploy_output        = jsondecode(azurerm_resource_group_template_deployment.container.output_content)
  container_ip_addr_output = contains(keys(local.arm_deploy_output), "containerIPv4Address") ? local.arm_deploy_output.containerIPv4Address : {}
  container_ip             = contains(keys(local.container_ip_addr_output), "value") ? local.container_ip_addr_output.value : "<unknown>"
}

output "container_ip" {
  value = local.container_ip
}

output "azure_portal_url" {
  value = "${local.portal_url}/#@${local.tenant_id}/resource${local.resource_id}"
}

