# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform from "TTA"
resource "aws_eks_cluster" "cluster" {
  bootstrap_self_managed_addons = false
  deletion_protection           = false
  enabled_cluster_log_types     = []
  force_update_version          = null
  name                          = "TTA"
  region                        = "eu-west-1"
  role_arn                      = "arn:aws:iam::906510885253:role/TTA-cluster-role"
  tags                          = {}
  tags_all                      = {}
  version                       = "1.34"
  access_config {
    authentication_mode                         = "CONFIG_MAP"
    bootstrap_cluster_creator_admin_permissions = true
  }
  compute_config {
    enabled       = false
    node_pools    = []
    node_role_arn = null
  }
  kubernetes_network_config {
    ip_family         = "ipv4"
    service_ipv4_cidr = "10.100.0.0/16"
    elastic_load_balancing {
      enabled = false
    }
  }
  storage_config {
    block_storage {
      enabled = false
    }
  }
  upgrade_policy {
    support_type = "EXTENDED"
  }
  vpc_config {
    endpoint_private_access = false
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
    security_group_ids      = []
    subnet_ids              = ["subnet-035e75399b3c845c5", "subnet-050797e272ad03759", "subnet-0f35f059444e7369e"]
  }
}
