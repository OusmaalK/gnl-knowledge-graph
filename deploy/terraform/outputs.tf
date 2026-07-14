# ============================================================================
# Outputs Terraform
# ============================================================================

output "cluster_id" {
  description = "ID du cluster EKS"
  value       = module.eks.cluster_id
}

output "cluster_endpoint" {
  description = "Endpoint du cluster EKS"
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "cluster_security_group_id" {
  description = "ID du groupe de sécurité du cluster"
  value       = module.eks.cluster_security_group_id
}

output "kubeconfig" {
  description = "Configuration kubectl pour le cluster"
  value       = module.eks.kubeconfig
  sensitive   = true
}

output "region" {
  description = "Région AWS"
  value       = var.region
}

output "vpc_id" {
  description = "ID du VPC"
  value       = module.vpc.vpc_id
}

output "subnet_ids" {
  description = "IDs des sous-réseaux"
  value       = module.vpc.private_subnet_ids
}

output "rds_endpoint" {
  description = "Endpoint RDS"
  value       = module.rds.endpoint
  sensitive   = true
}

output "rds_database_name" {
  description = "Nom de la base de données RDS"
  value       = module.rds.database_name
}

output "bucket_name" {
  description = "Nom du bucket S3"
  value       = aws_s3_bucket.gnl_bucket.id
}

output "iam_role_arn" {
  description = "ARN du rôle IAM"
  value       = module.eks.iam_role_arn
}

output "grafana_url" {
  description = "URL Grafana"
  value       = "https://grafana.${var.domain_name}"
}

output "api_url" {
  description = "URL API"
  value       = "https://api.${var.domain_name}"
}

output "neo4j_url" {
  description = "URL Neo4j"
  value       = "bolt://neo4j-service.${var.environment}.svc.cluster.local:7687"
}

output "redis_url" {
  description = "URL Redis"
  value       = "redis://redis-service.${var.environment}.svc.cluster.local:6379"
}