"""
Test Suite 3: CJIS Compliance Rules Tests

Tests for CJIS Security Policy 5.9 compliance including:
- Password policy enforcement
- MFA requirements
- Session management
- Encryption requirements
- Audit logging
- Data retention
- Training requirements
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestPasswordPolicy:
    """Test CJIS password policy compliance"""
    
    def test_minimum_password_length(self):
        """Test minimum 8 character password requirement"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.password_policy["min_length"] == 8
    
    def test_password_complexity_requirements(self):
        """Test password complexity requirements"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.password_policy["require_uppercase"] is True
        assert layer.password_policy["require_lowercase"] is True
        assert layer.password_policy["require_number"] is True
        assert layer.password_policy["require_special"] is True
    
    def test_password_max_age(self):
        """Test 90-day password expiration"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.password_policy["max_age_days"] == 90
    
    def test_password_history(self):
        """Test password history enforcement"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.password_policy["history_count"] == 10


class TestMFAPolicy:
    """Test CJIS MFA policy compliance"""
    
    def test_mfa_required_for_remote_access(self):
        """Test MFA requirement for remote access"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.mfa_policy["required_for_remote"] is True
    
    def test_mfa_required_for_cji_access(self):
        """Test MFA requirement for CJI access"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.mfa_policy["required_for_cji"] is True
    
    def test_mfa_required_for_admin(self):
        """Test MFA requirement for admin functions"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.mfa_policy["required_for_admin"] is True


class TestSessionManagement:
    """Test CJIS session management compliance"""
    
    def test_idle_timeout(self):
        """Test 30-minute idle timeout"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.session_policy["idle_timeout_minutes"] == 30
    
    def test_max_session_duration(self):
        """Test maximum session duration"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.session_policy["max_session_hours"] == 12
    
    def test_session_compliance_check(self):
        """Test session compliance checking"""
        from app.infra.cjis_compliance import (
            CJISComplianceLayer,
            CJISUser,
        )
        
        layer = CJISComplianceLayer()
        
        user = CJISUser(
            user_id="test-user",
            username="officer_smith",
            role="PATROL_OFFICER",
            agency_ori="FL0500400",
            last_login=datetime.utcnow(),
            session_start=datetime.utcnow() - timedelta(hours=1),
            last_activity=datetime.utcnow() - timedelta(minutes=5),
        )
        
        layer.register_user(user)
        
        result = layer.check_compliance(
            user_id="test-user",
            action="query",
            context={"is_remote": False},
        )
        assert result is not None


class TestEncryptionRequirements:
    """Test CJIS encryption requirements"""
    
    def test_encryption_at_rest(self):
        """Test AES-256 encryption at rest requirement"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.encryption_policy["algorithm"] == "AES-256"
    
    def test_encryption_in_transit(self):
        """Test TLS 1.2+ requirement for data in transit"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.encryption_policy["min_tls_version"] == "1.2"


class TestAuditLogging:
    """Test CJIS audit logging requirements"""
    
    def test_cji_access_logging(self):
        """Test CJI access logging"""
        from app.infra.cjis_compliance import (
            CJISComplianceLayer,
            CJISQuery,
            CJISDataCategory,
        )
        
        layer = CJISComplianceLayer()
        
        query = CJISQuery(
            query_id="query-1",
            user_id="test-user",
            query_type="NCIC",
            data_category=CJISDataCategory.CRIMINAL_HISTORY,
            case_number="2024-001234",
            purpose="Investigation",
            timestamp=datetime.utcnow(),
        )
        
        result = layer.log_cji_query(query)
        assert result is not None
    
    def test_audit_log_retention(self):
        """Test 7-year audit log retention"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.audit_policy["retention_days"] == 2555
    
    def test_query_log_retrieval(self):
        """Test query log retrieval"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        logs = layer.get_query_log(limit=10)
        assert isinstance(logs, list)


class TestDataRetention:
    """Test CJIS data retention requirements"""
    
    def test_retention_limits_by_category(self):
        """Test data retention limits by category"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert "CRIMINAL_HISTORY" in layer.retention_limits
        assert "ARREST_RECORDS" in layer.retention_limits
        assert "INCIDENT_REPORTS" in layer.retention_limits


class TestTrainingRequirements:
    """Test CJIS training requirements"""
    
    def test_security_awareness_training(self):
        """Test security awareness training requirement"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.training_requirements["security_awareness_months"] == 12
    
    def test_cjis_certification_training(self):
        """Test CJIS certification training requirement"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.training_requirements["cjis_certification_months"] == 24


class TestAgencyConfiguration:
    """Test Riviera Beach agency configuration"""
    
    def test_agency_ori(self):
        """Test agency ORI configuration"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.agency_config["ori"] == "FL0500400"
    
    def test_agency_state(self):
        """Test agency state configuration"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert layer.agency_config["state"] == "FL"
    
    def test_agency_name(self):
        """Test agency name configuration"""
        from app.infra.cjis_compliance import CJISComplianceLayer
        
        layer = CJISComplianceLayer()
        
        assert "Riviera Beach" in layer.agency_config["name"]
