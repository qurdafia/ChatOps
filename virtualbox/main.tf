# main.tf - Terraform configuration to create a VirtualBox VM

# =================================================================
# TERRAFORM AND PROVIDER CONFIGURATION
# =================================================================
terraform {
  required_providers {
    virtualbox = {
      source  = "terra-farm/virtualbox"
      version = "0.2.2-alpha.1"
    }
  }
}


# =================================================================
# VIRTUAL MACHINE RESOURCE
# =================================================================
resource "virtualbox_vm" "node" {
  count = 2
  name  = format("node-%02d", count.index + 1)

  # CORRECTED: Switched to a more reliable and modern base image
  # that is known to work well with the provider.
  # image = "bento/ubuntu-22.04"
  image = "https://app.vagrantup.com/bento/boxes/ubuntu-22.04/versions/202401.17.0/providers/virtualbox.box"

  cpus   = 2
  memory = "512 mib"

  user_data = file("${path.module}/cloud-config.yml")

  network_adapter {
    # type = "nat"
    type = "hostonly"
    # IMPORTANT: Make sure this network adapter exists in VirtualBox.
    # You can check by going to File > Host Network Manager...
    host_interface = "VirtualBox Host-Only Ethernet Adapter #4"
  }
}

# output "IPAddr_Node_1" {
#   value       = virtualbox_vm.node[0].network_adapter[0].ipv4_address
#   description = "The IP address of the first node."
# }

# output "IPAddr_Node_2" {
#   value       = virtualbox_vm.node[1].network_adapter[0].ipv4_address
#   description = "The IP address of the second node."
# }
