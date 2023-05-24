variable "resource_group_location" {
  default     = "eastus"
  description = "Location of the resource group."
}

variable "resource_group_name_prefix" {
  default     = "blindbox"
  description = "Prefix of the resource group name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "container_registry_name_prefix" {
  default     = "blindboxregistry"
  description = "Name of the custom container registry."
}

variable "cpu_count" {
  default = 1
  description = "Number of vCPU to allocate for the blindbox."
}

variable "memory_in_gb" {
  default = 1
  description = "Amount of RAM (in GB) to allocate for the blindbox."
}

variable "image" {
  type        = string
  description = "The app docker image used within the blindbox."
}
