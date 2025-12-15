"""
Phase 39 Test Suite: Deployment Pipeline
Tests for verifying GitHub Actions workflow and deployment configuration.
"""

import pytest
import os
import yaml
from pathlib import Path


class TestDeploymentPipeline:
    """Test suite for deployment pipeline validation."""

    @pytest.fixture
    def workflow_path(self):
        """Get workflow file path."""
        return Path("/home/ubuntu/repos/g3ti-rtcc-platform/.github/workflows/prelaunch-preview-deploy.yml")

    def test_workflow_file_exists(self, workflow_path):
        """Test deployment workflow file exists."""
        assert workflow_path.exists(), "prelaunch-preview-deploy.yml not found"

    def test_workflow_is_valid_yaml(self, workflow_path):
        """Test workflow file is valid YAML."""
        content = workflow_path.read_text()
        try:
            workflow = yaml.safe_load(content)
            assert workflow is not None
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML: {e}")

    def test_workflow_has_name(self, workflow_path):
        """Test workflow has a name."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "name" in workflow
        assert "Pre-Launch" in workflow["name"] or "Preview" in workflow["name"]

    def test_workflow_has_triggers(self, workflow_path):
        """Test workflow has trigger events."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "on" in workflow
        assert isinstance(workflow["on"], (dict, list, str))

    def test_workflow_has_jobs(self, workflow_path):
        """Test workflow has jobs defined."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "jobs" in workflow
        assert len(workflow["jobs"]) > 0

    def test_system_validation_job_exists(self, workflow_path):
        """Test system-validation job exists."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "system-validation" in workflow["jobs"]

    def test_build_frontend_job_exists(self, workflow_path):
        """Test build-frontend job exists."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "build-frontend" in workflow["jobs"]

    def test_build_backend_job_exists(self, workflow_path):
        """Test build-backend job exists."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "build-backend" in workflow["jobs"]

    def test_integration_tests_job_exists(self, workflow_path):
        """Test integration-tests job exists."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "integration-tests" in workflow["jobs"]

    def test_deploy_frontend_job_exists(self, workflow_path):
        """Test deploy-frontend job exists."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "deploy-frontend" in workflow["jobs"]

    def test_deploy_backend_job_exists(self, workflow_path):
        """Test deploy-backend job exists."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "deploy-backend" in workflow["jobs"]

    def test_generate_report_job_exists(self, workflow_path):
        """Test generate-report job exists."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "generate-report" in workflow["jobs"]

    def test_workflow_has_env_vars(self, workflow_path):
        """Test workflow has environment variables."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "env" in workflow
        assert "NODE_VERSION" in workflow["env"]
        assert "PYTHON_VERSION" in workflow["env"]

    def test_workflow_uses_checkout_action(self, workflow_path):
        """Test workflow uses checkout action."""
        content = workflow_path.read_text()
        assert "actions/checkout@v4" in content

    def test_workflow_uses_python_setup(self, workflow_path):
        """Test workflow uses Python setup action."""
        content = workflow_path.read_text()
        assert "actions/setup-python@v5" in content

    def test_workflow_uses_node_setup(self, workflow_path):
        """Test workflow uses Node.js setup action."""
        content = workflow_path.read_text()
        assert "actions/setup-node@v4" in content

    def test_workflow_references_vercel(self, workflow_path):
        """Test workflow references Vercel for frontend deployment."""
        content = workflow_path.read_text()
        assert "VERCEL" in content or "vercel" in content.lower()

    def test_workflow_references_fly(self, workflow_path):
        """Test workflow references Fly.io for backend deployment."""
        content = workflow_path.read_text()
        assert "FLY" in content or "fly" in content.lower()

    def test_workflow_has_preview_urls(self, workflow_path):
        """Test workflow outputs preview URLs."""
        content = workflow_path.read_text()
        assert "preview" in content.lower()
        assert "url" in content.lower()

    def test_workflow_runs_pytest(self, workflow_path):
        """Test workflow runs pytest for tests."""
        content = workflow_path.read_text()
        assert "pytest" in content

    def test_workflow_has_stress_test_job(self, workflow_path):
        """Test workflow has optional stress test job."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        assert "stress-test" in workflow["jobs"]

    def test_workflow_dispatch_inputs(self, workflow_path):
        """Test workflow has manual dispatch inputs."""
        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)
        
        if "workflow_dispatch" in workflow.get("on", {}):
            dispatch = workflow["on"]["workflow_dispatch"]
            if "inputs" in dispatch:
                assert "deploy_frontend" in dispatch["inputs"] or "deploy_backend" in dispatch["inputs"]
