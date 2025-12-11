terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
  
  backend "s3" {
    bucket         = "rtcc-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-gov-east-1"
    encrypt        = true
    dynamodb_table = "rtcc-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "G3TI-RTCC-UIP"
      Environment = var.environment
      Agency      = "Riviera Beach PD"
      Compliance  = "CJIS"
      ManagedBy   = "Terraform"
    }
  }
}

locals {
  name_prefix = "rtcc-${var.environment}"
  
  common_tags = {
    Project     = "G3TI-RTCC-UIP"
    Environment = var.environment
    Agency      = "Riviera Beach PD"
    Compliance  = "CJIS"
  }
}

module "vpc" {
  source = "./modules/vpc"
  
  name_prefix         = local.name_prefix
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  private_subnets     = var.private_subnets
  public_subnets      = var.public_subnets
  database_subnets    = var.database_subnets
  enable_nat_gateway  = true
  single_nat_gateway  = false
  enable_vpn_gateway  = true
  
  tags = local.common_tags
}

module "eks" {
  source = "./modules/eks"
  
  cluster_name    = "${local.name_prefix}-cluster"
  cluster_version = var.eks_cluster_version
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  
  node_groups = {
    general = {
      desired_size = 3
      min_size     = 2
      max_size     = 10
      instance_types = ["m5.xlarge"]
      capacity_type  = "ON_DEMAND"
    }
    
    gpu = {
      desired_size = 2
      min_size     = 1
      max_size     = 6
      instance_types = ["p3.2xlarge"]
      capacity_type  = "ON_DEMAND"
      labels = {
        "gpu" = "true"
      }
      taints = [{
        key    = "nvidia.com/gpu"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }
  
  tags = local.common_tags
}

module "rds" {
  source = "./modules/rds"
  
  identifier     = "${local.name_prefix}-postgres"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.rds_instance_class
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_encrypted     = true
  
  db_name  = "rtcc"
  username = "rtcc_admin"
  port     = 5432
  
  vpc_id                = module.vpc.vpc_id
  subnet_ids            = module.vpc.database_subnet_ids
  vpc_security_group_ids = [module.security_groups.rds_sg_id]
  
  multi_az               = true
  backup_retention_period = 35
  deletion_protection    = true
  
  performance_insights_enabled = true
  monitoring_interval         = 60
  
  tags = local.common_tags
}

module "elasticache" {
  source = "./modules/elasticache"
  
  cluster_id           = "${local.name_prefix}-redis"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = var.redis_node_type
  num_cache_nodes      = 3
  parameter_group_name = "default.redis7.cluster.on"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  security_group_ids = [module.security_groups.redis_sg_id]
  
  automatic_failover_enabled = true
  multi_az_enabled          = true
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = local.common_tags
}

module "elasticsearch" {
  source = "./modules/elasticsearch"
  
  domain_name    = "${local.name_prefix}-es"
  engine_version = "OpenSearch_2.11"
  
  cluster_config = {
    instance_type            = var.es_instance_type
    instance_count           = 3
    dedicated_master_enabled = true
    dedicated_master_type    = "m5.large.search"
    dedicated_master_count   = 3
    zone_awareness_enabled   = true
    availability_zone_count  = 3
  }
  
  ebs_options = {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 500
    iops        = 3000
    throughput  = 250
  }
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  security_group_ids = [module.security_groups.es_sg_id]
  
  encrypt_at_rest_enabled = true
  node_to_node_encryption = true
  
  tags = local.common_tags
}

module "security_groups" {
  source = "./modules/security_groups"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  vpc_cidr    = var.vpc_cidr
  
  tags = local.common_tags
}

module "alb" {
  source = "./modules/alb"
  
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  
  vpc_id          = module.vpc.vpc_id
  subnets         = module.vpc.public_subnet_ids
  security_groups = [module.security_groups.alb_sg_id]
  
  enable_deletion_protection = true
  enable_http2              = true
  idle_timeout              = 60
  
  access_logs = {
    bucket  = module.s3.logs_bucket_id
    prefix  = "alb-logs"
    enabled = true
  }
  
  tags = local.common_tags
}

module "s3" {
  source = "./modules/s3"
  
  name_prefix = local.name_prefix
  
  buckets = {
    logs = {
      versioning = true
      encryption = true
      lifecycle_rules = [{
        id      = "log-retention"
        enabled = true
        expiration = {
          days = 2555
        }
      }]
    }
    
    backups = {
      versioning = true
      encryption = true
      lifecycle_rules = [{
        id      = "backup-retention"
        enabled = true
        transition = [{
          days          = 30
          storage_class = "GLACIER"
        }]
        expiration = {
          days = 2555
        }
      }]
    }
    
    data_lake = {
      versioning = true
      encryption = true
    }
  }
  
  tags = local.common_tags
}

module "secrets_manager" {
  source = "./modules/secrets_manager"
  
  name_prefix = local.name_prefix
  
  secrets = {
    database = {
      description = "RDS database credentials"
      rotation_days = 30
    }
    redis = {
      description = "Redis authentication"
      rotation_days = 30
    }
    jwt = {
      description = "JWT signing secret"
      rotation_days = 90
    }
    encryption = {
      description = "Data encryption key"
      rotation_days = 365
    }
  }
  
  tags = local.common_tags
}

module "cloudwatch" {
  source = "./modules/cloudwatch"
  
  name_prefix = local.name_prefix
  
  log_groups = {
    api_gateway = {
      retention_days = 365
    }
    ai_engine = {
      retention_days = 365
    }
    security = {
      retention_days = 2555
    }
    audit = {
      retention_days = 2555
    }
  }
  
  alarms = {
    high_cpu = {
      metric_name = "CPUUtilization"
      threshold   = 80
      period      = 300
    }
    high_memory = {
      metric_name = "MemoryUtilization"
      threshold   = 85
      period      = 300
    }
    api_errors = {
      metric_name = "5XXError"
      threshold   = 10
      period      = 60
    }
  }
  
  tags = local.common_tags
}

module "iam" {
  source = "./modules/iam"
  
  name_prefix = local.name_prefix
  
  eks_cluster_name = module.eks.cluster_name
  
  roles = {
    eks_node = {
      description = "EKS node IAM role"
      policies = [
        "arn:aws-us-gov:iam::aws:policy/AmazonEKSWorkerNodePolicy",
        "arn:aws-us-gov:iam::aws:policy/AmazonEKS_CNI_Policy",
        "arn:aws-us-gov:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
      ]
    }
    
    api_gateway = {
      description = "API Gateway service role"
      policies = []
    }
    
    ai_engine = {
      description = "AI Engine service role"
      policies = []
    }
  }
  
  tags = local.common_tags
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.endpoint
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.elasticache.endpoint
}

output "elasticsearch_endpoint" {
  description = "Elasticsearch endpoint"
  value       = module.elasticsearch.endpoint
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.dns_name
}
