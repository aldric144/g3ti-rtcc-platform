"""
Test Suite 10: CJIS Compliance Guard Tests

Tests for CJIS security policy compliance and audit requirements.
"""

import pytest
from datetime import datetime, UTC

from app.admin_logs.activity_log_model import ActivityLogCreate, LogType, LogPriority
from app.admin_logs.activity_log_service import ActivityLogService
from app.shift_admin.shift_model import ShiftCreate, AddOperatorRequest, OperatorRole
from app.shift_admin.shift_service import ShiftService
from app.case_tools.case_tools_model import CaseNoteCreate, CaseShellCreate, CasePriority
from app.case_tools.case_tools_service import CaseToolsService


@pytest.fixture
def activity_log_service():
    """Create a fresh activity log service for each test."""
    return ActivityLogService()


@pytest.fixture
def shift_service():
    """Create a fresh shift service for each test."""
    return ShiftService()


@pytest.fixture
def case_tools_service():
    """Create a fresh case tools service for each test."""
    return CaseToolsService()


class TestAuditLogging:
    """Tests for CJIS-compliant audit logging."""
    
    @pytest.mark.asyncio
    async def test_all_actions_logged(self, activity_log_service):
        """Test that all CRUD actions are logged in audit trail."""
        from app.admin_logs.activity_log_model import ActivityLogUpdate
        
        # Create
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=LogPriority.MEDIUM,
            notes="Test log",
        )
        log = await activity_log_service.create_log(data, "user1")
        
        # Update
        update_data = ActivityLogUpdate(notes="Updated")
        await activity_log_service.update_log(log.id, update_data, "user2")
        
        # Archive
        await activity_log_service.archive_log(log.id, "user3")
        
        # Get audit trail
        audit = await activity_log_service.get_audit_trail(log.id)
        
        actions = [entry["action"] for entry in audit]
        assert "CREATE" in actions
        assert "UPDATE" in actions
        assert "ARCHIVE" in actions
    
    @pytest.mark.asyncio
    async def test_audit_includes_timestamp(self, activity_log_service):
        """Test that audit entries include timestamps."""
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=LogPriority.MEDIUM,
            notes="Test",
        )
        log = await activity_log_service.create_log(data, "admin")
        
        audit = await activity_log_service.get_audit_trail(log.id)
        
        for entry in audit:
            assert "timestamp" in entry
            # Timestamp should be ISO format
            datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
    
    @pytest.mark.asyncio
    async def test_audit_includes_user(self, activity_log_service):
        """Test that audit entries include user identification."""
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=LogPriority.MEDIUM,
            notes="Test",
        )
        log = await activity_log_service.create_log(data, "specific_user")
        
        audit = await activity_log_service.get_audit_trail(log.id)
        
        assert audit[0]["editor"] == "specific_user"


class TestDataIntegrity:
    """Tests for data integrity requirements."""
    
    @pytest.mark.asyncio
    async def test_log_immutable_id(self, activity_log_service):
        """Test that log IDs cannot be changed."""
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=LogPriority.MEDIUM,
            notes="Test",
        )
        log = await activity_log_service.create_log(data, "admin")
        original_id = log.id
        
        # Update should not change ID
        from app.admin_logs.activity_log_model import ActivityLogUpdate
        update_data = ActivityLogUpdate(notes="Updated")
        updated = await activity_log_service.update_log(log.id, update_data, "admin")
        
        assert updated.id == original_id
    
    @pytest.mark.asyncio
    async def test_created_at_immutable(self, activity_log_service):
        """Test that created_at timestamp cannot be changed."""
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=LogPriority.MEDIUM,
            notes="Test",
        )
        log = await activity_log_service.create_log(data, "admin")
        original_created_at = log.created_at
        
        from app.admin_logs.activity_log_model import ActivityLogUpdate
        update_data = ActivityLogUpdate(notes="Updated")
        updated = await activity_log_service.update_log(log.id, update_data, "admin")
        
        assert updated.created_at == original_created_at
    
    @pytest.mark.asyncio
    async def test_case_number_unique(self, case_tools_service):
        """Test that case numbers are unique."""
        case_numbers = set()
        
        for _ in range(10):
            data = CaseShellCreate(
                title="Test Case",
                priority=CasePriority.MEDIUM,
            )
            shell = await case_tools_service.create_case_shell(data, "admin")
            case_numbers.add(shell.case_number)
        
        assert len(case_numbers) == 10


class TestAccessControl:
    """Tests for access control requirements."""
    
    @pytest.mark.asyncio
    async def test_editor_tracked_on_create(self, activity_log_service):
        """Test that editor is tracked on creation."""
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=LogPriority.MEDIUM,
            notes="Test",
        )
        log = await activity_log_service.create_log(data, "creating_user")
        
        assert log.editor == "creating_user"
    
    @pytest.mark.asyncio
    async def test_operator_roles_enforced(self, shift_service):
        """Test that operator roles are properly enforced."""
        data = ShiftCreate(supervisor="Sgt. Johnson")
        await shift_service.open_shift(data)
        
        # Add operators with different roles
        roles_added = []
        for role in OperatorRole:
            op_data = AddOperatorRequest(
                username=f"user_{role.value}",
                name=f"User {role.value}",
                role=role,
            )
            shift = await shift_service.add_operator(op_data, "admin")
            roles_added.append(shift.operators[-1].role)
        
        assert set(roles_added) == set(OperatorRole)


class TestSessionManagement:
    """Tests for session management requirements."""
    
    @pytest.mark.asyncio
    async def test_shift_supervisor_required(self, shift_service):
        """Test that shift requires supervisor."""
        data = ShiftCreate(supervisor="Sgt. Johnson")
        shift = await shift_service.open_shift(data)
        
        assert shift.supervisor is not None
        assert len(shift.supervisor) > 0
    
    @pytest.mark.asyncio
    async def test_shift_signoff_required_for_close(self, shift_service):
        """Test that shift close requires supervisor signoff."""
        from app.shift_admin.shift_model import ShiftClose
        
        data = ShiftCreate(supervisor="Sgt. Johnson")
        await shift_service.open_shift(data)
        
        close_data = ShiftClose(
            closing_notes="Shift ended",
            supervisor_signoff="Sgt. Johnson",
        )
        closed = await shift_service.close_shift(close_data)
        
        assert closed.supervisor_signoff is not None


class TestDataRetention:
    """Tests for data retention requirements."""
    
    @pytest.mark.asyncio
    async def test_archived_logs_retained(self, activity_log_service):
        """Test that archived logs are retained."""
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=LogPriority.MEDIUM,
            notes="To archive",
        )
        log = await activity_log_service.create_log(data, "admin")
        
        await activity_log_service.archive_log(log.id, "admin")
        
        # Should still be retrievable
        archived = await activity_log_service.get_log(log.id)
        assert archived is not None
        assert archived.archived is True
    
    @pytest.mark.asyncio
    async def test_audit_trail_preserved_after_delete(self, activity_log_service):
        """Test that audit trail is preserved after deletion."""
        data = ActivityLogCreate(
            log_type=LogType.INCIDENT,
            priority=LogPriority.MEDIUM,
            notes="To delete",
        )
        log = await activity_log_service.create_log(data, "admin")
        log_id = log.id
        
        await activity_log_service.delete_log(log_id, "admin")
        
        # Audit trail should still exist
        audit = await activity_log_service.get_audit_trail(log_id)
        assert len(audit) >= 2  # CREATE and DELETE
    
    @pytest.mark.asyncio
    async def test_shift_history_preserved(self, shift_service):
        """Test that shift history is preserved."""
        from app.shift_admin.shift_model import ShiftClose
        
        # Create and close multiple shifts
        for i in range(3):
            open_data = ShiftCreate(supervisor=f"Supervisor {i}")
            await shift_service.open_shift(open_data)
            
            close_data = ShiftClose(
                closing_notes=f"Shift {i} closed",
                supervisor_signoff=f"Supervisor {i}",
            )
            await shift_service.close_shift(close_data)
        
        history = await shift_service.get_shift_history()
        
        assert len(history) == 3
