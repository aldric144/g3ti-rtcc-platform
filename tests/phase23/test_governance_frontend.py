"""
Phase 23: Frontend Governance UI Tests
"""

import pytest
import os


class TestCityGovernancePageStructure:
    """Tests for city governance page structure."""

    def test_main_page_exists(self):
        """Test main city governance page exists."""
        page_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/page.tsx",
        )
        assert os.path.exists(page_path)

    def test_city_operations_dashboard_exists(self):
        """Test CityOperationsDashboard component exists."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/CityOperationsDashboard.tsx",
        )
        assert os.path.exists(component_path)

    def test_resource_optimization_panel_exists(self):
        """Test ResourceOptimizationPanel component exists."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ResourceOptimizationPanel.tsx",
        )
        assert os.path.exists(component_path)

    def test_scenario_simulator_exists(self):
        """Test ScenarioSimulator component exists."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ScenarioSimulator.tsx",
        )
        assert os.path.exists(component_path)

    def test_governance_kpi_dashboard_exists(self):
        """Test GovernanceKPIDashboard component exists."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/GovernanceKPIDashboard.tsx",
        )
        assert os.path.exists(component_path)


class TestMainPageContent:
    """Tests for main page content."""

    def test_page_has_use_client_directive(self):
        """Test page has 'use client' directive."""
        page_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/page.tsx",
        )
        with open(page_path, "r") as f:
            content = f.read()
            assert '"use client"' in content or "'use client'" in content

    def test_page_imports_components(self):
        """Test page imports all required components."""
        page_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/page.tsx",
        )
        with open(page_path, "r") as f:
            content = f.read()
            assert "CityOperationsDashboard" in content
            assert "ResourceOptimizationPanel" in content
            assert "ScenarioSimulator" in content
            assert "GovernanceKPIDashboard" in content

    def test_page_has_tab_navigation(self):
        """Test page has tab navigation."""
        page_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/page.tsx",
        )
        with open(page_path, "r") as f:
            content = f.read()
            assert "activeTab" in content or "setActiveTab" in content


class TestCityOperationsDashboardContent:
    """Tests for CityOperationsDashboard component content."""

    def test_component_has_city_health_score(self):
        """Test component displays city health score."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/CityOperationsDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "City Health" in content or "cityHealth" in content

    def test_component_has_resource_efficiency(self):
        """Test component displays resource efficiency."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/CityOperationsDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Resource Efficiency" in content or "resourceEfficiency" in content

    def test_component_has_recommended_deployments(self):
        """Test component displays recommended deployments."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/CityOperationsDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Recommended" in content or "decisions" in content

    def test_component_has_alerts_feed(self):
        """Test component displays alerts feed."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/CityOperationsDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Alert" in content or "alerts" in content


class TestResourceOptimizationPanelContent:
    """Tests for ResourceOptimizationPanel component content."""

    def test_component_has_drag_and_drop(self):
        """Test component has drag and drop functionality."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ResourceOptimizationPanel.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "draggable" in content or "onDrag" in content

    def test_component_has_optimization_button(self):
        """Test component has run optimization button."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ResourceOptimizationPanel.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Run Optimization" in content or "runOptimization" in content

    def test_component_has_zones(self):
        """Test component displays zones."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ResourceOptimizationPanel.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "zone" in content.lower()

    def test_component_has_explainability_drawer(self):
        """Test component has explainability drawer."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ResourceOptimizationPanel.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Explain" in content or "explainability" in content.lower()


class TestScenarioSimulatorContent:
    """Tests for ScenarioSimulator component content."""

    def test_component_has_templates(self):
        """Test component displays scenario templates."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ScenarioSimulator.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "template" in content.lower()

    def test_component_has_variable_sliders(self):
        """Test component has variable sliders."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ScenarioSimulator.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "range" in content.lower() or "slider" in content.lower()

    def test_component_has_run_simulation_button(self):
        """Test component has run simulation button."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ScenarioSimulator.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Run Simulation" in content or "runSimulation" in content

    def test_component_has_timeline(self):
        """Test component displays timeline."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ScenarioSimulator.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "timeline" in content.lower()

    def test_component_has_outcome_paths(self):
        """Test component displays outcome paths."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ScenarioSimulator.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "outcome" in content.lower() or "path" in content.lower()


class TestGovernanceKPIDashboardContent:
    """Tests for GovernanceKPIDashboard component content."""

    def test_component_has_response_time_chart(self):
        """Test component displays response time chart."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/GovernanceKPIDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Response Time" in content or "responseTime" in content

    def test_component_has_patrol_efficiency(self):
        """Test component displays patrol efficiency."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/GovernanceKPIDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Patrol" in content or "patrol" in content

    def test_component_has_fire_ems_coverage(self):
        """Test component displays fire/EMS coverage."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/GovernanceKPIDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Fire" in content or "EMS" in content

    def test_component_has_utility_uptime(self):
        """Test component displays utility uptime."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/GovernanceKPIDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Utility" in content or "uptime" in content.lower()

    def test_component_has_traffic_congestion(self):
        """Test component displays traffic congestion."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/GovernanceKPIDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Traffic" in content or "Congestion" in content

    def test_component_has_budget_metrics(self):
        """Test component displays budget metrics."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/GovernanceKPIDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "Budget" in content or "budget" in content


class TestComponentExports:
    """Tests for component exports."""

    def test_city_operations_dashboard_default_export(self):
        """Test CityOperationsDashboard has default export."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/CityOperationsDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "export default" in content

    def test_resource_optimization_panel_default_export(self):
        """Test ResourceOptimizationPanel has default export."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ResourceOptimizationPanel.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "export default" in content

    def test_scenario_simulator_default_export(self):
        """Test ScenarioSimulator has default export."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/ScenarioSimulator.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "export default" in content

    def test_governance_kpi_dashboard_default_export(self):
        """Test GovernanceKPIDashboard has default export."""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "../../frontend/app/city-governance/components/GovernanceKPIDashboard.tsx",
        )
        with open(component_path, "r") as f:
            content = f.read()
            assert "export default" in content
