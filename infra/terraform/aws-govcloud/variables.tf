variable "aws_region" {
  description = "AWS GovCloud region"
  type        = string
  default     = "us-gov-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be production, staging, or development."
  }
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-gov-east-1a", "us-gov-east-1b", "us-gov-east-1c"]
}

variable "private_subnets" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "database_subnets" {
  description = "Database subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]
}

variable "eks_cluster_version" {
  description = "EKS cluster version"
  type        = string
  default     = "1.28"
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.xlarge"
}

variable "redis_node_type" {
  description = "Redis node type"
  type        = string
  default     = "cache.r6g.large"
}

variable "es_instance_type" {
  description = "Elasticsearch instance type"
  type        = string
  default     = "r6g.large.search"
}

variable "enable_multi_region" {
  description = "Enable multi-region deployment"
  type        = bool
  default     = true
}

variable "secondary_region" {
  description = "Secondary region for failover"
  type        = string
  default     = "us-gov-west-1"
}

variable "cjis_compliance_level" {
  description = "CJIS compliance level"
  type        = string
  default     = "strict"
  
  validation {
    condition     = contains(["strict", "standard"], var.cjis_compliance_level)
    error_message = "CJIS compliance level must be strict or standard."
  }
}

variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 35
  
  validation {
    condition     = var.backup_retention_days >= 7 && var.backup_retention_days <= 35
    error_message = "Backup retention must be between 7 and 35 days."
  }
}

variable "log_retention_days" {
  description = "Log retention period in days"
  type        = number
  default     = 2555
}

variable "enable_waf" {
  description = "Enable WAF for ALB"
  type        = bool
  default     = true
}

variable "enable_shield" {
  description = "Enable AWS Shield Advanced"
  type        = bool
  default     = true
}

variable "allowed_ip_ranges" {
  description = "Allowed IP ranges for access"
  type        = list(string)
  default     = []
}

variable "riviera_beach_config" {
  description = "Riviera Beach specific configuration"
  type = object({
    city_code    = string
    population   = number
    area_sq_miles = number
    coordinates = object({
      lat = number
      lon = number
    })
  })
  default = {
    city_code     = "33404"
    population    = 37964
    area_sq_miles = 9.76
    coordinates = {
      lat = 26.7753
      lon = -80.0583
    }
  }
}
