# Get the resulting azure portal url
data "azurerm_client_config" "current" {}

locals {
  tenant_id   = data.azurerm_client_config.current.tenant_id
  portal_url  = "https://portal.azure.com"
  resource_id = azurerm_resource_group_template_deployment.container.id
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
