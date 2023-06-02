resource "random_pet" "rg_name" {
  prefix = var.resource_group_name_prefix
}

resource "azurerm_resource_group" "rg" {
  location = var.resource_group_location
  name     = random_pet.rg_name.id
}

# Create container registry
resource "random_integer" "container_registery_suffix" {
  min = 0
  max = 1000000
}

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

# Create virtual network
resource "azurerm_virtual_network" "vnet" {
  name                = "vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

# Create subnet
resource "azurerm_subnet" "subnet" {
  name                 = "subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Create public IPs
resource "azurerm_public_ip" "public_ip" {
  name                = "public_ip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Dynamic"
}

# Create Network Security Group and rule
resource "azurerm_network_security_group" "nsg" {
  name                = "nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# Create network interface
resource "azurerm_network_interface" "nic" {
  name                = "nic"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "nic_config"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.public_ip.id
  }
}

# Connect the security group to the network interface
resource "azurerm_network_interface_security_group_association" "gassoc" {
  network_interface_id      = azurerm_network_interface.nic.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

# Create (and display) an SSH key
resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Create virtual machine
resource "azurerm_linux_virtual_machine" "cvm" {
  name                  = "cvm"
  location              = azurerm_resource_group.rg.location
  resource_group_name   = azurerm_resource_group.rg.name
  network_interface_ids = [azurerm_network_interface.nic.id]
  size                  = var.vm_size
  secure_boot_enabled   = true
  vtpm_enabled          = true

  os_disk {
    name                     = "main_disk"
    caching                  = "ReadWrite"
    storage_account_type     = "Standard_LRS"
    security_encryption_type = "DiskWithVMGuestState"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-confidential-vm-focal"
    sku       = "20_04-lts-cvm"
    version   = "latest"
  }

  computer_name                   = "cvm"
  admin_username                  = "azureuser"
  disable_password_authentication = true

  admin_ssh_key {
    username   = "azureuser"
    public_key = tls_private_key.ssh_key.public_key_openssh
  }
}
