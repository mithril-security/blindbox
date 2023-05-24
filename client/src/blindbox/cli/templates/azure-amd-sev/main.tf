# Some constants
locals {
  container_ports = [
    {
      port     = 80
      protocol = "TCP"
    },
    {
      port     = 8080
      protocol = "TCP"
    },
  ]
  blindbox_image = "mithrilsecuritysas/blindbox:sev"
}

# All resources are part of a new resource group
resource "random_pet" "rg_name" {
  prefix = var.resource_group_name_prefix
}

resource "azurerm_resource_group" "rg" {
  location = var.resource_group_location
  name     = random_pet.rg_name.id
}

resource "random_integer" "container_registery_suffix" {
  min = 0
  max = 1000000
}

# Create a dedicated container registry
resource "azurerm_container_registry" "cr" {
  name                = "${var.container_registry_name_prefix}${random_integer.container_registery_suffix.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled = true
}

# Retag local docker image before push
resource "docker_tag" "image" {
  source_image = var.image
  target_image = "${azurerm_container_registry.cr.login_server}/${var.image}"
}

# Push local docker image to the dedicated registry
resource "null_resource" "docker_push" {
  provisioner "local-exec" {
    environment = {
      LOGIN_SERVER   = azurerm_container_registry.cr.login_server,
      ADMIN_USERNAME = azurerm_container_registry.cr.admin_username,
      ADMIN_PASSWORD = nonsensitive(azurerm_container_registry.cr.admin_password),
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
    azurerm_container_registry.cr,
  ]

  triggers = {
    image          = var.image,
    retag          = docker_tag.image.source_image_id,
    LOGIN_SERVER   = azurerm_container_registry.cr.login_server,
    ADMIN_USERNAME = azurerm_container_registry.cr.admin_username,
    ADMIN_PASSWORD = azurerm_container_registry.cr.admin_password,
    IMAGE          = docker_tag.image.target_image
  }
}

# Container group
# We use a template deployment (ARM file) since confidential-computing is not
# supported by the azurerm terraform provider.
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
#            "confidentialComputeProperties" : {
#              "ccePolicy" : data.local_file.cce_policy.content
#            },
            "containers" : [
              {
                "name" : "blindbox",
                "properties" : {
                  "image" : local.blindbox_image,
                  "ports" : local.container_ports,
                  "resources" : {
                    "requests" : {
                      "cpu" : var.cpu_count,
                      "memoryInGB" : var.memory_in_gb
                    }
                  },
                  "securityContext" : {
                    "privileged" : true
                  },
                  "environmentVariables": [
                    {
                      "name": "INNER_IMAGE",
                      "value": var.image,
                    }
                  ]
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
                "server" : azurerm_container_registry.cr.login_server,
                "username" : azurerm_container_registry.cr.admin_username,
                "password" : azurerm_container_registry.cr.admin_password
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

  lifecycle {
    # Updating the deployment in-place does not work when the ACR
    # is redeployed, apparently.
    replace_triggered_by = [azurerm_container_registry.cr]
  }

  deployment_mode = "Incremental"
}
