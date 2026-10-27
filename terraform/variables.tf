
variable "location" {
  description = "Azure region for project resources"
  type        = string
  default = "indiasouthcentral"
}

variable "project_name" {
  description = "Prefix for Azure resource names"
  type        = string
  default     = "expense-tracker"
}

variable "admin_username" {
  description = "Linux VM administrator username"
  type        = string
  default     = "azureuser"
}

variable "admin_ssh_public_key" {
  description = "SSH public key for Linux VM access"
  type        = string
}

variable "admin_source_ip" {
  description = "Public IPv4 address allowed to SSH into the VM"
  type        = string
}
