variable "resource_group_location" {
  type        = string
  default     = "eastus"
  description = "Location of the resource group."
}

variable "resource_group_name_prefix" {
  type        = string
  default     = "blindbox"
  description = "Prefix of the resource group name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "container_registry_name_prefix" {
  type        = string
  default     = "blindboxregistry"
  description = "Name of the custom container registry."
}

variable "image" {
  type        = string
  description = "The app docker image used within the blindbox."
}

variable "vm_size" {
  type        = string
  default     = "Standard_DC2as_v5"
  description = "The type of VM to use."
}
