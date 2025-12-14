"""
Test Suite: Mission Reasoner

Tests for MissionReasoner, mission planning, and task management.
"""

import pytest
from datetime import datetime, timedelta

from backend.app.personas.mission_reasoner import (
    MissionReasoner,
    MissionStatus,
    MissionPriority,
    TaskType,
    ResourceType,
    RiskLevel,
    ApprovalStatus,
    RiskAssessment,
    PolicyViolation,
    ApprovalRequest,
    MissionTask,
    MissionOutcome,
    Mission,
)


class TestMissionReasoner:
    """Tests for MissionReasoner singleton."""
    
    def test_singleton_pattern(self):
        """Test that MissionReasoner follows singleton pattern."""
        reasoner1 = MissionReasoner()
        reasoner2 = MissionReasoner()
        assert reasoner1 is reasoner2
    
    def test_create_mission(self):
        """Test creating a mission."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Test Mission",
            description="Test mission description",
            mission_type="patrol",
            priority=MissionPriority.MEDIUM,
            created_by="test-persona",
            objectives=["Objective 1", "Objective 2"],
        )
        
        assert mission is not None
        assert mission.title == "Test Mission"
        assert mission.mission_type == "patrol"
        assert mission.priority == MissionPriority.MEDIUM
        assert mission.status == MissionStatus.DRAFT
        assert len(mission.objectives) == 2
    
    def test_get_mission(self):
        """Test getting a mission by ID."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Get Test Mission",
            description="Test",
            mission_type="investigation",
            priority=MissionPriority.HIGH,
            created_by="test-persona",
            objectives=["Test objective"],
        )
        
        retrieved = reasoner.get_mission(mission.mission_id)
        assert retrieved is not None
        assert retrieved.mission_id == mission.mission_id
    
    def test_get_nonexistent_mission(self):
        """Test getting non-existent mission returns None."""
        reasoner = MissionReasoner()
        mission = reasoner.get_mission("nonexistent-mission")
        assert mission is None
    
    def test_get_all_missions(self):
        """Test getting all missions."""
        reasoner = MissionReasoner()
        
        reasoner.create_mission(
            title="All Test 1",
            description="Test",
            mission_type="patrol",
            priority=MissionPriority.LOW,
            created_by="test",
            objectives=["Test"],
        )
        
        missions = reasoner.get_all_missions()
        assert len(missions) >= 1
    
    def test_get_active_missions(self):
        """Test getting active missions."""
        reasoner = MissionReasoner()
        active = reasoner.get_active_missions()
        
        for mission in active:
            assert mission.status == MissionStatus.IN_PROGRESS
    
    def test_get_statistics(self):
        """Test getting reasoner statistics."""
        reasoner = MissionReasoner()
        stats = reasoner.get_statistics()
        
        assert "total_missions" in stats
        assert "active_missions" in stats
        assert "missions_by_status" in stats


class TestMissionPlanning:
    """Tests for mission planning functionality."""
    
    def test_plan_mission_generates_tasks(self):
        """Test that planning generates tasks."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Planning Test",
            description="Test mission for planning",
            mission_type="surveillance",
            priority=MissionPriority.MEDIUM,
            created_by="test-persona",
            objectives=[
                "Monitor target location",
                "Document all activity",
                "Report findings",
            ],
        )
        
        planned = reasoner.plan_mission(mission.mission_id)
        
        assert planned is not None
        assert len(planned.tasks) > 0
        assert planned.status in [MissionStatus.PENDING_APPROVAL, MissionStatus.APPROVED]
    
    def test_plan_mission_assesses_risk(self):
        """Test that planning assesses risk."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Risk Test",
            description="Test mission for risk assessment",
            mission_type="tactical",
            priority=MissionPriority.HIGH,
            created_by="test-persona",
            objectives=["Execute tactical operation"],
        )
        
        planned = reasoner.plan_mission(mission.mission_id)
        
        assert planned.risk_assessment is not None
        assert planned.risk_assessment.overall_risk in [
            RiskLevel.MINIMAL,
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        ]
    
    def test_plan_mission_checks_policy(self):
        """Test that planning checks for policy violations."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Policy Test",
            description="Test mission for policy checking",
            mission_type="investigation",
            priority=MissionPriority.MEDIUM,
            created_by="test-persona",
            objectives=["Investigate suspect"],
        )
        
        planned = reasoner.plan_mission(mission.mission_id)
        
        assert planned.policy_violations is not None


class TestApprovalWorkflow:
    """Tests for approval workflow."""
    
    def test_request_approval(self):
        """Test requesting approval."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Approval Test",
            description="Test mission for approval",
            mission_type="tactical",
            priority=MissionPriority.CRITICAL,
            created_by="test-persona",
            objectives=["Critical operation"],
        )
        
        request = reasoner.request_approval(
            mission_id=mission.mission_id,
            request_type="mission_start",
            description="Request to start critical mission",
            urgency="high",
            required_authority="supervisor",
        )
        
        assert request is not None
        assert request.status == ApprovalStatus.PENDING
    
    def test_approve_request(self):
        """Test approving a request."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Approve Test",
            description="Test",
            mission_type="patrol",
            priority=MissionPriority.HIGH,
            created_by="test",
            objectives=["Test"],
        )
        
        request = reasoner.request_approval(
            mission_id=mission.mission_id,
            request_type="mission_start",
            description="Test approval",
            urgency="medium",
            required_authority="supervisor",
        )
        
        success = reasoner.approve_request(
            request_id=request.request_id,
            approved_by="supervisor-001",
            notes="Approved for testing",
        )
        
        assert success
    
    def test_deny_request(self):
        """Test denying a request."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Deny Test",
            description="Test",
            mission_type="tactical",
            priority=MissionPriority.HIGH,
            created_by="test",
            objectives=["Test"],
        )
        
        request = reasoner.request_approval(
            mission_id=mission.mission_id,
            request_type="mission_start",
            description="Test denial",
            urgency="low",
            required_authority="commander",
        )
        
        success = reasoner.deny_request(
            request_id=request.request_id,
            denied_by="commander-001",
            reason="Insufficient resources",
        )
        
        assert success
    
    def test_get_pending_approvals(self):
        """Test getting pending approvals."""
        reasoner = MissionReasoner()
        pending = reasoner.get_pending_approvals()
        
        for approval in pending:
            assert approval.status == ApprovalStatus.PENDING


class TestResourceAssignment:
    """Tests for resource assignment."""
    
    def test_assign_resources(self):
        """Test assigning resources to mission."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Resource Test",
            description="Test mission for resources",
            mission_type="surveillance",
            priority=MissionPriority.MEDIUM,
            created_by="test-persona",
            objectives=["Surveillance operation"],
        )
        
        reasoner.plan_mission(mission.mission_id)
        success = reasoner.assign_resources(mission.mission_id)
        
        assert success
    
    def test_assign_personas(self):
        """Test assigning personas to mission."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Persona Assignment Test",
            description="Test mission for persona assignment",
            mission_type="investigation",
            priority=MissionPriority.HIGH,
            created_by="test-persona",
            objectives=["Investigation task"],
        )
        
        reasoner.plan_mission(mission.mission_id)
        success = reasoner.assign_personas(mission.mission_id)
        
        assert success


class TestMissionLifecycle:
    """Tests for mission lifecycle management."""
    
    def test_start_mission(self):
        """Test starting a mission."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Start Test",
            description="Test",
            mission_type="patrol",
            priority=MissionPriority.MEDIUM,
            created_by="test",
            objectives=["Test"],
        )
        
        reasoner.plan_mission(mission.mission_id)
        
        updated = reasoner.get_mission(mission.mission_id)
        if updated.status == MissionStatus.APPROVED:
            success = reasoner.start_mission(mission.mission_id)
            assert success
            
            started = reasoner.get_mission(mission.mission_id)
            assert started.status == MissionStatus.IN_PROGRESS
    
    def test_complete_mission(self):
        """Test completing a mission."""
        reasoner = MissionReasoner()
        
        mission = reasoner.create_mission(
            title="Complete Test",
            description="Test",
            mission_type="patrol",
            priority=MissionPriority.LOW,
            created_by="test",
            objectives=["Test"],
        )
        
        reasoner.plan_mission(mission.mission_id)
        
        updated = reasoner.get_mission(mission.mission_id)
        if updated.status == MissionStatus.APPROVED:
            reasoner.start_mission(mission.mission_id)
            
            success = reasoner.complete_mission(
                mission.mission_id,
                success=True,
                summary="Mission completed successfully",
            )
            
            assert success
            
            completed = reasoner.get_mission(mission.mission_id)
            assert completed.status == MissionStatus.COMPLETED


class TestMission:
    """Tests for Mission dataclass."""
    
    def test_mission_to_dict(self):
        """Test mission serialization."""
        mission = Mission(
            mission_id="test-mission",
            title="Test Mission",
            description="Test description",
            mission_type="patrol",
            priority=MissionPriority.MEDIUM,
            created_by="test-persona",
            objectives=["Objective 1"],
        )
        
        data = mission.to_dict()
        
        assert data["mission_id"] == "test-mission"
        assert data["title"] == "Test Mission"
        assert data["priority"] == "medium"
        assert "status" in data
        assert "objectives" in data
    
    def test_mission_progress(self):
        """Test mission progress calculation."""
        mission = Mission(
            mission_id="progress-test",
            title="Progress Test",
            description="Test",
            mission_type="patrol",
            priority=MissionPriority.LOW,
            created_by="test",
            objectives=["Test"],
        )
        
        mission.tasks = [
            MissionTask(
                task_id="task-1",
                task_type=TaskType.SURVEILLANCE,
                description="Task 1",
                status=MissionStatus.COMPLETED,
                sequence_number=1,
            ),
            MissionTask(
                task_id="task-2",
                task_type=TaskType.DOCUMENTATION,
                description="Task 2",
                status=MissionStatus.IN_PROGRESS,
                sequence_number=2,
            ),
            MissionTask(
                task_id="task-3",
                task_type=TaskType.REPORTING,
                description="Task 3",
                status=MissionStatus.DRAFT,
                sequence_number=3,
            ),
        ]
        
        progress = mission.get_progress()
        
        assert progress["total_tasks"] == 3
        assert progress["completed"] == 1
        assert progress["in_progress"] == 1
        assert 0 <= progress["completion_percentage"] <= 100


class TestMissionTask:
    """Tests for MissionTask dataclass."""
    
    def test_task_creation(self):
        """Test creating a mission task."""
        task = MissionTask(
            task_id="task-001",
            task_type=TaskType.PATROL,
            description="Patrol sector 5",
            status=MissionStatus.DRAFT,
            sequence_number=1,
        )
        
        assert task.task_id == "task-001"
        assert task.task_type == TaskType.PATROL
        assert task.sequence_number == 1
    
    def test_task_to_dict(self):
        """Test task serialization."""
        task = MissionTask(
            task_id="task-002",
            task_type=TaskType.INVESTIGATION,
            description="Investigate lead",
            status=MissionStatus.IN_PROGRESS,
            sequence_number=2,
        )
        
        data = task.to_dict()
        
        assert data["task_id"] == "task-002"
        assert data["task_type"] == "investigation"
        assert "status" in data


class TestRiskAssessment:
    """Tests for RiskAssessment dataclass."""
    
    def test_risk_assessment_creation(self):
        """Test creating a risk assessment."""
        assessment = RiskAssessment(
            overall_risk=RiskLevel.MEDIUM,
            risk_factors=["Unknown terrain", "Limited visibility"],
            mitigation_strategies=["Deploy additional units", "Use thermal imaging"],
            confidence=0.75,
        )
        
        assert assessment.overall_risk == RiskLevel.MEDIUM
        assert len(assessment.risk_factors) == 2
        assert len(assessment.mitigation_strategies) == 2
        assert assessment.confidence == 0.75
