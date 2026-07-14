# Infrastructure as Code - Terraform
# Fournisseurs AWS

terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.0.0"
    }
  }
  
  backend "s3" {
    bucket = "gnl-terraform-state"
    key    = "gnl-knowledge-graph/terraform.tfstate"
    region = "eu-west-1"
  }
}

provider "aws" {
  region = var.region
  
  default_tags {
    tags = {
      Project     = "GNL Knowledge Graph"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# VPC
module "vpc" {
  source = "./modules/network"
  
  vpc_cidr           = var.vpc_cidr
  environment        = var.environment
  availability_zones = var.availability_zones
}

# EKS Cluster
module "eks" {
  source = "./modules/compute"
  
  cluster_name    = "${var.project_name}-${var.environment}"
  cluster_version = "1.27"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  
  node_groups = {
    main = {
      instance_types = var.instance_types
      desired_size   = var.desired_size
      max_size       = var.max_size
      min_size       = var.min_size
    }
  }
}

# RDS pour métadonnées
module "rds" {
  source = "./modules/database"
  
  database_name     = "gnl_metadata"
  database_user     = var.database_user
  database_password = var.database_password
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  instance_class    = var.db_instance_class
}

# Outputs
output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "kubeconfig" {
  value = module.eks.kubeconfig
  sensitive = true
}