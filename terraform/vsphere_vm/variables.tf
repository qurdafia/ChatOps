variable "vsphere_user" {}
variable "vsphere_password" {}
variable "vsphere_server" {}

variable "vm_name" {
  type        = string
  description = "Name for the virtual machine."
}
variable "num_vcpus" {
  type        = number
  description = "Number of vCPUs for the VM."
}
variable "memory_gb" {
  type        = number
  description = "Memory in GB for the VM."
}
variable "image_name" {
  type        = string
  description = "Name of the template/image to clone."
}