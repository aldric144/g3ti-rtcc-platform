"""
Test Suite 6: Kubernetes Manifest Validation Tests

Tests for Kubernetes manifest validation including:
- YAML syntax validation
- Resource specification
- Security configurations
- Network policies
- Service definitions
"""

import pytest
import os
import yaml
from pathlib import Path


class TestNamespaceManifest:
    """Test namespace manifest validation"""
    
    def test_namespace_file_exists(self):
        """Test that namespace manifest exists"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/namespace.yaml")
        assert manifest_path.exists()
    
    def test_namespace_yaml_valid(self):
        """Test that namespace YAML is valid"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/namespace.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        assert len(docs) > 0
        assert docs[0]["kind"] == "Namespace"
    
    def test_namespace_labels(self):
        """Test namespace has required labels"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/namespace.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        namespace = docs[0]
        labels = namespace["metadata"]["labels"]
        
        assert "compliance" in labels
        assert labels["compliance"] == "cjis"


class TestDeploymentManifests:
    """Test deployment manifest validation"""
    
    def test_api_gateway_deployment_exists(self):
        """Test that API gateway deployment exists"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/api-gateway-deployment.yaml")
        assert manifest_path.exists()
    
    def test_api_gateway_replicas(self):
        """Test API gateway has minimum replicas"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/api-gateway-deployment.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        deployment = docs[0]
        assert deployment["spec"]["replicas"] >= 3
    
    def test_api_gateway_health_probes(self):
        """Test API gateway has health probes"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/api-gateway-deployment.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        deployment = docs[0]
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        
        assert "livenessProbe" in container
        assert "readinessProbe" in container
    
    def test_ai_engine_deployment_exists(self):
        """Test that AI engine deployment exists"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/ai-engine-deployment.yaml")
        assert manifest_path.exists()
    
    def test_ai_engine_gpu_resources(self):
        """Test AI engine has GPU resources"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/ai-engine-deployment.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        deployment = docs[0]
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        resources = container["resources"]
        
        assert "nvidia.com/gpu" in resources["requests"]


class TestSecurityConfigurations:
    """Test security configurations in manifests"""
    
    def test_non_root_user(self):
        """Test containers run as non-root"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/api-gateway-deployment.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        deployment = docs[0]
        security_context = deployment["spec"]["template"]["spec"]["securityContext"]
        
        assert security_context["runAsNonRoot"] is True
    
    def test_secrets_from_secret_refs(self):
        """Test secrets are loaded from SecretKeyRef"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/api-gateway-deployment.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        deployment = docs[0]
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        
        secret_env_vars = [
            env for env in container["env"]
            if "valueFrom" in env and "secretKeyRef" in env["valueFrom"]
        ]
        
        assert len(secret_env_vars) > 0


class TestIngressManifest:
    """Test ingress manifest validation"""
    
    def test_ingress_file_exists(self):
        """Test that ingress manifest exists"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/ingress.yaml")
        assert manifest_path.exists()
    
    def test_ingress_tls_enabled(self):
        """Test ingress has TLS enabled"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/ingress.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        ingress = docs[0]
        assert "tls" in ingress["spec"]
    
    def test_ingress_security_headers(self):
        """Test ingress has security headers"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/ingress.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        ingress = docs[0]
        annotations = ingress["metadata"]["annotations"]
        
        assert "nginx.ingress.kubernetes.io/configuration-snippet" in annotations


class TestNetworkPolicies:
    """Test network policy configurations"""
    
    def test_network_policy_exists(self):
        """Test that network policy exists"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/ingress.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        network_policies = [d for d in docs if d and d.get("kind") == "NetworkPolicy"]
        assert len(network_policies) > 0
    
    def test_network_policy_egress_rules(self):
        """Test network policy has egress rules"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/ingress.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        network_policies = [d for d in docs if d and d.get("kind") == "NetworkPolicy"]
        
        if network_policies:
            policy = network_policies[0]
            assert "Egress" in policy["spec"]["policyTypes"]


class TestSecretsManifest:
    """Test secrets manifest validation"""
    
    def test_secrets_file_exists(self):
        """Test that secrets manifest exists"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/secrets.yaml")
        assert manifest_path.exists()
    
    def test_external_secrets_configured(self):
        """Test external secrets are configured"""
        manifest_path = Path("/home/ubuntu/repos/g3ti-rtcc-platform/infra/kubernetes/secrets.yaml")
        
        with open(manifest_path) as f:
            docs = list(yaml.safe_load_all(f))
        
        external_secrets = [d for d in docs if d and d.get("kind") == "ExternalSecret"]
        assert len(external_secrets) > 0
