locals {
  image_tag = "testsev:v1.2"
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


# Build a docker image locally.
resource "docker_image" "image" {
  name = "${azurerm_container_registry.acr.login_server}/${local.image_tag}"
  build {
    context    = ".."
    dockerfile = "./sev/sev.dockerfile"
    tag        = ["${azurerm_container_registry.acr.login_server}/${local.image_tag}"]
  }
}

resource "null_resource" "docker_push" {
  provisioner "local-exec" {
    environment = {
      LOGIN_SERVER   = nonsensitive(azurerm_container_registry.acr.login_server),
      ADMIN_USERNAME = nonsensitive(azurerm_container_registry.acr.admin_username),
      ADMIN_PASSWORD = azurerm_container_registry.acr.admin_password,
      IMAGE          = docker_image.image.name
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
    docker_image.image
  ]
}

resource "null_resource" "make_cce_policy" {
  provisioner "local-exec" {
    environment = {
      DOCKER_IMAGE = docker_image.image.name
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
                  "image" : docker_image.image.name,
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

  # parameters_content = jsonencode({})

  deployment_mode = "Incremental"
}

# output "container_ip" {
#   value = jsondecode(azurerm_resource_group_template_deployment.container.output_content).containerIPv4Address.value
# }

output "cce_policy" {
  value = data.local_file.cce_policy.content
}

