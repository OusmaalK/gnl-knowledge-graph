# Variables Terraform

variable "project_name" {
  description = "Nom du projet"
  type        = string
  default     = "gnl-knowledge-graph"
}

variable "environment" {
  description = "Environnement (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "L'environnement doit être dev, staging ou prod."
  }
}

variable "region" {
  description = "Région AWS"
  type        = string
  default     = "eu-west-1"
}

variable "vpc_cidr" {
  description = "CIDR du VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Zones de disponibilité"
  type        = list(string)
  default     = ["eu-west-1a", "eu-west-1b"]
}

variable "instance_types" {
  description = "Types d'instances pour EKS"
  type        = list(string)
  default     = ["t3.medium", "t3.large"]
}

variable "desired_size" {
  description = "Taille désirée du cluster EKS"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Taille max du cluster EKS"
  type        = number
  default     = 5
}

variable "min_size" {
  description = "Taille min du cluster EKS"
  type        = number
  default     = 1
}

variable "database_user" {
  description = "Utilisateur RDS"
  type        = string
  sensitive   = true
}

variable "database_password" {
  description = "Mot de passe RDS"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "Classe d'instance RDS"
  type        = string
  default     = "db.t3.medium"
}