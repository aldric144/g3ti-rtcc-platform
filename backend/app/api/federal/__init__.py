"""
G3TI RTCC-UIP Federal Readiness API Endpoints
Phase 11: REST API for federal data exports, NCIC stubs, eTrace, SAR, and CJIS compliance
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.federal.common import (
    FederalAuditLogger,
    FederalDataCategory,
    FederalExportStatus,
    FederalMessageType,
    FederalSystem,
    federal_audit_logger,
)
from app.federal.ndex import (
    NDExExportManager,
    NDExRoleType,
    ndex_export_manager,
)
from app.federal.ncic import (
    NCICQueryManager,
    NCICQueryType,
    ncic_query_manager,
)
from app.federal.etrace import (
    ETraceExportManager,
    ETraceRequestType,
    etrace_export_manager,
)
from app.federal.dhs_sar import (
    SARBehaviorCategory,
    SARBehaviorIndicator,
    SARManager,
    SARThreatLevel,
    sar_manager,
)
from app.federal.cjis import (
    CJISAccessControl,
    CJISAuditAction,
    CJISAuditLogger,
    CJISComplianceManager,
    CJISResourceType,
    cjis_audit_logger,
    cjis_compliance_manager,
)
from app.federal.secure_packaging import (
    SecurePackagingManager,
    secure_packaging_manager,
)


router = APIRouter(prefix="/federal", tags=["Federal Readiness"])


# ============================================================================
# Request/Response Models
# ============================================================================

class NDExPersonExportRequest(BaseModel):
    """Request to export person to N-DEx"""
    person_data: dict[str, Any]
    role_type: str = "Subject"


class NDExIncidentExportRequest(BaseModel):
    """Request to export incident to N-DEx"""
    incident_data: dict[str, Any]
    include_related: bool = True


class NCICVehicleQueryRequest(BaseModel):
    """Request for NCIC vehicle query stub"""
    vin: str | None = None
    license_plate: str | None = None
    license_state: str | None = None
    make: str | None = None
    model: str | None = None
    year: str | None = None
    color: str | None = None
    purpose: str | None = None


class NCICPersonQueryRequest(BaseModel):
    """Request for NCIC person query stub"""
    last_name: str | None = None
    first_name: str | None = None
    date_of_birth: str | None = None
    ssn: str | None = None
    drivers_license: str | None = None
    drivers_license_state: str | None = None
    fbi_number: str | None = None
    purpose: str | None = None


class NCICGunQueryRequest(BaseModel):
    """Request for NCIC gun query stub"""
    serial_number: str | None = None
    make: str | None = None
    model: str | None = None
    caliber: str | None = None
    gun_type: str | None = None
    purpose: str | None = None


class ETraceExportRequest(BaseModel):
    """Request to export weapon to eTrace"""
    weapon_data: dict[str, Any]
    recovery_data: dict[str, Any]
    crime_code: str | None = None
    incident_id: str | None = None
    case_number: str | None = None
    possessor_data: dict[str, Any] | None = None
    notes: str | None = None


class ETraceIncidentExportRequest(BaseModel):
    """Request to export incident weapons to eTrace"""
    incident_data: dict[str, Any]


class SARCreateRequest(BaseModel):
    """Request to create SAR"""
    behavior_category: str
    activity_date: str
    activity_time: str | None = None
    activity_location: dict[str, Any]
    narrative: str
    behavior_indicators: list[str] | None = None
    subjects: list[dict[str, Any]] | None = None
    vehicles: list[dict[str, Any]] | None = None
    threat_assessment: str = "unknown"
    related_incidents: list[str] | None = None
    additional_notes: str | None = None


class SARUpdateRequest(BaseModel):
    """Request to update SAR"""
    narrative: str | None = None
    threat_assessment: str | None = None
    behavior_category: str | None = None
    behavior_indicators: list[str] | None = None
    additional_notes: str | None = None


class SARSubmitRequest(BaseModel):
    """Request to submit SAR"""
    approver_name: str


class FederalExportResponse(BaseModel):
    """Response for federal export"""
    success: bool
    export_id: str | None = None
    message: str
    data: dict[str, Any] | None = None
    validation_errors: list[str] | None = None
    validation_warnings: list[str] | None = None


class NCICStubResponse(BaseModel):
    """Response for NCIC stub query"""
    success: bool
    query_id: str
    response_id: str
    message: str
    is_stub: bool = True
    sample_data: dict[str, Any] | None = None
    validation_errors: list[str] | None = None


class AuditLogResponse(BaseModel):
    """Response for audit log query"""
    success: bool
    total_entries: int
    entries: list[dict[str, Any]]


class ComplianceReportResponse(BaseModel):
    """Response for compliance report"""
    success: bool
    report: dict[str, Any]


# ============================================================================
# Helper Functions
# ============================================================================

def get_user_info(request: Request) -> tuple[str, str, str]:
    """Extract user info from request (placeholder for auth integration)"""
    # In production, extract from JWT token
    user_id = request.headers.get("X-User-ID", "system")
    user_name = request.headers.get("X-User-Name", "System User")
    agency_id = request.headers.get("X-Agency-ID", "DEFAULT_ORI")
    return user_id, user_name, agency_id


def get_client_ip(request: Request) -> str | None:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


# ============================================================================
# N-DEx Export Endpoints
# ============================================================================

@router.get("/ndex/export/person/{person_id}")
async def export_person_to_ndex(
    person_id: str,
    request: Request,
    role_type: str = Query("Subject", description="Person role type"),
) -> FederalExportResponse:
    """Export person to N-DEx format"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="ndex_export",
        resource_type=CJISResourceType.NDEX_EXPORT,
        resource_id=person_id,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    # For demo, create sample person data
    person_data = {
        "id": person_id,
        "last_name": "Sample",
        "first_name": "Person",
        "date_of_birth": "1990-01-15",
        "sex": "M",
        "race": "W",
    }

    try:
        role = NDExRoleType(role_type)
    except ValueError:
        role = NDExRoleType.SUBJECT

    package = ndex_export_manager.export_person(
        person_data=person_data,
        role_type=role,
        agency_id=agency_id,
        user_id=user_id,
        user_name=user_name,
    )

    # Mask sensitive data
    masked_payload = cjis_compliance_manager.mask_federal_data(package.payload)

    return FederalExportResponse(
        success=True,
        export_id=package.id,
        message="Person exported to N-DEx format successfully",
        data=masked_payload,
    )


@router.post("/ndex/export/person")
async def export_person_data_to_ndex(
    export_request: NDExPersonExportRequest,
    request: Request,
) -> FederalExportResponse:
    """Export person data to N-DEx format"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="ndex_export",
        resource_type=CJISResourceType.NDEX_EXPORT,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    try:
        role = NDExRoleType(export_request.role_type)
    except ValueError:
        role = NDExRoleType.SUBJECT

    package = ndex_export_manager.export_person(
        person_data=export_request.person_data,
        role_type=role,
        agency_id=agency_id,
        user_id=user_id,
        user_name=user_name,
    )

    # Validate
    validation = ndex_export_manager.validate_export(package.id)

    # Mask sensitive data
    masked_payload = cjis_compliance_manager.mask_federal_data(package.payload)

    return FederalExportResponse(
        success=validation.is_valid,
        export_id=package.id,
        message="Person export created" if validation.is_valid else "Validation failed",
        data=masked_payload,
        validation_errors=validation.errors if not validation.is_valid else None,
        validation_warnings=validation.warnings,
    )


@router.get("/ndex/export/incident/{incident_id}")
async def export_incident_to_ndex(
    incident_id: str,
    request: Request,
    include_related: bool = Query(True, description="Include related entities"),
) -> FederalExportResponse:
    """Export incident to N-DEx format"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="ndex_export",
        resource_type=CJISResourceType.NDEX_EXPORT,
        resource_id=incident_id,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    # For demo, create sample incident data
    incident_data = {
        "id": incident_id,
        "incident_number": f"INC-{incident_id[:8]}",
        "incident_date": "2024-01-15",
        "type": "criminal",
        "agency_ori": agency_id,
        "location": {
            "street": "123 Main St",
            "city": "Sample City",
            "state": "FL",
        },
        "narrative": "Sample incident narrative for demonstration.",
    }

    package = ndex_export_manager.export_incident(
        incident_data=incident_data,
        agency_id=agency_id,
        user_id=user_id,
        user_name=user_name,
        include_related=include_related,
    )

    # Mask sensitive data
    masked_payload = cjis_compliance_manager.mask_federal_data(package.payload)

    return FederalExportResponse(
        success=True,
        export_id=package.id,
        message="Incident exported to N-DEx format successfully",
        data=masked_payload,
    )


@router.post("/ndex/export/incident")
async def export_incident_data_to_ndex(
    export_request: NDExIncidentExportRequest,
    request: Request,
) -> FederalExportResponse:
    """Export incident data to N-DEx format"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="ndex_export",
        resource_type=CJISResourceType.NDEX_EXPORT,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    package = ndex_export_manager.export_incident(
        incident_data=export_request.incident_data,
        agency_id=agency_id,
        user_id=user_id,
        user_name=user_name,
        include_related=export_request.include_related,
    )

    # Validate
    validation = ndex_export_manager.validate_export(package.id)

    # Mask sensitive data
    masked_payload = cjis_compliance_manager.mask_federal_data(package.payload)

    return FederalExportResponse(
        success=validation.is_valid,
        export_id=package.id,
        message="Incident export created" if validation.is_valid else "Validation failed",
        data=masked_payload,
        validation_errors=validation.errors if not validation.is_valid else None,
        validation_warnings=validation.warnings,
    )


@router.get("/ndex/exports")
async def list_ndex_exports(
    request: Request,
    limit: int = Query(100, le=1000),
) -> dict[str, Any]:
    """List N-DEx exports for agency"""
    user_id, user_name, agency_id = get_user_info(request)

    exports = ndex_export_manager.get_exports_by_agency(agency_id, limit)

    return {
        "success": True,
        "total": len(exports),
        "exports": [e.to_dict() for e in exports],
    }


# ============================================================================
# NCIC Query Stub Endpoints (NON-OPERATIONAL)
# ============================================================================

@router.post("/ncic/query/vehicle")
async def ncic_vehicle_query_stub(
    query_request: NCICVehicleQueryRequest,
    request: Request,
) -> NCICStubResponse:
    """
    NCIC Vehicle Query STUB (NON-OPERATIONAL)

    This is a non-operational NCIC request stub for readiness purposes only.
    No actual NCIC query is performed.
    """
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="ncic_query",
        resource_type=CJISResourceType.NCIC_QUERY,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    query_params = query_request.model_dump(exclude_none=True)
    query_params.pop("purpose", None)

    query, response = ncic_query_manager.create_vehicle_query(
        agency_ori=agency_id,
        officer_name=user_name,
        query_params=query_params,
        user_id=user_id,
        purpose=query_request.purpose,
    )

    validation_errors = None
    if query.validation_result and not query.validation_result.is_valid:
        validation_errors = query.validation_result.errors

    return NCICStubResponse(
        success=True,
        query_id=query.id,
        response_id=response.id,
        message=response.message,
        is_stub=True,
        sample_data=response.sample_data,
        validation_errors=validation_errors,
    )


@router.post("/ncic/query/person")
async def ncic_person_query_stub(
    query_request: NCICPersonQueryRequest,
    request: Request,
) -> NCICStubResponse:
    """
    NCIC Person Query STUB (NON-OPERATIONAL)

    This is a non-operational NCIC request stub for readiness purposes only.
    No actual NCIC query is performed.
    """
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="ncic_query",
        resource_type=CJISResourceType.NCIC_QUERY,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    query_params = query_request.model_dump(exclude_none=True)
    query_params.pop("purpose", None)

    query, response = ncic_query_manager.create_person_query(
        agency_ori=agency_id,
        officer_name=user_name,
        query_params=query_params,
        user_id=user_id,
        purpose=query_request.purpose,
    )

    validation_errors = None
    if query.validation_result and not query.validation_result.is_valid:
        validation_errors = query.validation_result.errors

    return NCICStubResponse(
        success=True,
        query_id=query.id,
        response_id=response.id,
        message=response.message,
        is_stub=True,
        sample_data=response.sample_data,
        validation_errors=validation_errors,
    )


@router.post("/ncic/query/gun")
async def ncic_gun_query_stub(
    query_request: NCICGunQueryRequest,
    request: Request,
) -> NCICStubResponse:
    """
    NCIC Gun Query STUB (NON-OPERATIONAL)

    This is a non-operational NCIC request stub for readiness purposes only.
    No actual NCIC query is performed.
    """
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="ncic_query",
        resource_type=CJISResourceType.NCIC_QUERY,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    query_params = query_request.model_dump(exclude_none=True)
    query_params.pop("purpose", None)

    query, response = ncic_query_manager.create_gun_query(
        agency_ori=agency_id,
        officer_name=user_name,
        query_params=query_params,
        user_id=user_id,
        purpose=query_request.purpose,
    )

    validation_errors = None
    if query.validation_result and not query.validation_result.is_valid:
        validation_errors = query.validation_result.errors

    return NCICStubResponse(
        success=True,
        query_id=query.id,
        response_id=response.id,
        message=response.message,
        is_stub=True,
        sample_data=response.sample_data,
        validation_errors=validation_errors,
    )


@router.get("/ncic/readiness")
async def get_ncic_readiness_status(request: Request) -> dict[str, Any]:
    """Get NCIC readiness status"""
    return ncic_query_manager.get_readiness_status()


# ============================================================================
# ATF eTrace Export Endpoints
# ============================================================================

@router.get("/etrace/export/weapon/{weapon_id}")
async def export_weapon_to_etrace(
    weapon_id: str,
    request: Request,
) -> FederalExportResponse:
    """Export weapon to eTrace format"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="etrace_export",
        resource_type=CJISResourceType.ETRACE_EXPORT,
        resource_id=weapon_id,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    # For demo, create sample weapon data
    weapon_data = {
        "id": weapon_id,
        "type": "pistol",
        "make": "Sample Manufacturer",
        "model": "Model X",
        "caliber": "9mm",
        "serial_number": "ABC123456",
    }

    recovery_data = {
        "recovery_date": "2024-01-15",
        "city": "Sample City",
        "state": "FL",
        "context": "crime",
    }

    package = etrace_export_manager.export_weapon(
        weapon_id=weapon_id,
        weapon_data=weapon_data,
        recovery_data=recovery_data,
        agency_id=agency_id,
        user_id=user_id,
        user_name=user_name,
    )

    # Mask sensitive data
    masked_payload = cjis_compliance_manager.mask_federal_data(package.payload)

    return FederalExportResponse(
        success=package.status == FederalExportStatus.READY,
        export_id=package.id,
        message="Weapon exported to eTrace format successfully",
        data=masked_payload,
    )


@router.post("/etrace/export/weapon")
async def export_weapon_data_to_etrace(
    export_request: ETraceExportRequest,
    request: Request,
) -> FederalExportResponse:
    """Export weapon data to eTrace format"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="etrace_export",
        resource_type=CJISResourceType.ETRACE_EXPORT,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    trace_request = etrace_export_manager.create_trace_request(
        weapon_data=export_request.weapon_data,
        recovery_data=export_request.recovery_data,
        agency_ori=agency_id,
        officer_name=user_name,
        user_id=user_id,
        crime_code=export_request.crime_code,
        incident_id=export_request.incident_id,
        case_number=export_request.case_number,
        possessor_data=export_request.possessor_data,
        notes=export_request.notes,
    )

    validation_errors = None
    validation_warnings = None
    if trace_request.validation_result:
        if not trace_request.validation_result.is_valid:
            validation_errors = trace_request.validation_result.errors
        validation_warnings = trace_request.validation_result.warnings

    # Mask sensitive data
    masked_data = cjis_compliance_manager.mask_federal_data(trace_request.to_dict())

    return FederalExportResponse(
        success=trace_request.status == FederalExportStatus.VALIDATED,
        export_id=trace_request.id,
        message="eTrace request created" if trace_request.status == FederalExportStatus.VALIDATED else "Validation failed",
        data=masked_data,
        validation_errors=validation_errors,
        validation_warnings=validation_warnings,
    )


@router.get("/etrace/export/incident/{incident_id}")
async def export_incident_weapons_to_etrace(
    incident_id: str,
    request: Request,
) -> dict[str, Any]:
    """Export all weapons from incident to eTrace format"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="etrace_export",
        resource_type=CJISResourceType.ETRACE_EXPORT,
        resource_id=incident_id,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    # For demo, create sample incident with weapons
    incident_data = {
        "id": incident_id,
        "date": "2024-01-15",
        "city": "Sample City",
        "state": "FL",
        "weapons": [
            {
                "id": "weapon-1",
                "type": "pistol",
                "make": "Sample",
                "model": "Model A",
                "caliber": "9mm",
                "serial_number": "SN12345",
            },
        ],
    }

    packages = etrace_export_manager.export_incident_weapons(
        incident_id=incident_id,
        incident_data=incident_data,
        agency_id=agency_id,
        user_id=user_id,
        user_name=user_name,
    )

    return {
        "success": True,
        "incident_id": incident_id,
        "total_weapons": len(packages),
        "exports": [
            {
                "export_id": p.id,
                "status": p.status.value,
            }
            for p in packages
        ],
    }


@router.get("/etrace/statistics")
async def get_etrace_statistics(request: Request) -> dict[str, Any]:
    """Get eTrace export statistics"""
    user_id, user_name, agency_id = get_user_info(request)
    return etrace_export_manager.get_statistics(agency_id)


# ============================================================================
# DHS SAR Endpoints
# ============================================================================

@router.post("/sar/create")
async def create_sar(
    sar_request: SARCreateRequest,
    request: Request,
) -> FederalExportResponse:
    """Create a new Suspicious Activity Report"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="sar_submit",
        resource_type=CJISResourceType.SAR_REPORT,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    try:
        behavior_category = SARBehaviorCategory(sar_request.behavior_category)
    except ValueError:
        behavior_category = SARBehaviorCategory.OTHER

    behavior_indicators = None
    if sar_request.behavior_indicators:
        behavior_indicators = []
        for bi in sar_request.behavior_indicators:
            try:
                behavior_indicators.append(SARBehaviorIndicator(bi))
            except ValueError:
                pass

    try:
        threat_level = SARThreatLevel(sar_request.threat_assessment)
    except ValueError:
        threat_level = SARThreatLevel.UNKNOWN

    report = sar_manager.create_sar(
        agency_ori=agency_id,
        officer_name=user_name,
        user_id=user_id,
        behavior_category=behavior_category,
        activity_date=sar_request.activity_date,
        activity_time=sar_request.activity_time,
        activity_location=sar_request.activity_location,
        narrative=sar_request.narrative,
        behavior_indicators=behavior_indicators,
        subjects=sar_request.subjects,
        vehicles=sar_request.vehicles,
        threat_assessment=threat_level,
        related_incidents=sar_request.related_incidents,
        additional_notes=sar_request.additional_notes,
    )

    validation_errors = None
    validation_warnings = None
    if report.validation_result:
        if not report.validation_result.is_valid:
            validation_errors = report.validation_result.errors
        validation_warnings = report.validation_result.warnings

    # Mask sensitive data
    masked_data = cjis_compliance_manager.mask_federal_data(report.to_dict())

    return FederalExportResponse(
        success=report.validation_result.is_valid if report.validation_result else True,
        export_id=report.id,
        message=f"SAR {report.sar_number} created successfully",
        data=masked_data,
        validation_errors=validation_errors,
        validation_warnings=validation_warnings,
    )


@router.get("/sar/{sar_id}")
async def get_sar(
    sar_id: str,
    request: Request,
) -> FederalExportResponse:
    """Get SAR by ID"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="sar_submit",
        resource_type=CJISResourceType.SAR_REPORT,
        resource_id=sar_id,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    report = sar_manager.get_sar(sar_id)
    if not report:
        raise HTTPException(status_code=404, detail="SAR not found")

    # Mask sensitive data
    masked_data = cjis_compliance_manager.mask_federal_data(report.to_dict())

    return FederalExportResponse(
        success=True,
        export_id=report.id,
        message=f"SAR {report.sar_number} retrieved",
        data=masked_data,
    )


@router.put("/sar/{sar_id}")
async def update_sar(
    sar_id: str,
    update_request: SARUpdateRequest,
    request: Request,
) -> FederalExportResponse:
    """Update an existing SAR"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="sar_submit",
        resource_type=CJISResourceType.SAR_REPORT,
        resource_id=sar_id,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    updates = update_request.model_dump(exclude_none=True)
    report = sar_manager.update_sar(sar_id, updates)

    if not report:
        raise HTTPException(status_code=404, detail="SAR not found or cannot be updated")

    # Mask sensitive data
    masked_data = cjis_compliance_manager.mask_federal_data(report.to_dict())

    return FederalExportResponse(
        success=True,
        export_id=report.id,
        message=f"SAR {report.sar_number} updated",
        data=masked_data,
    )


@router.post("/sar/{sar_id}/submit")
async def submit_sar(
    sar_id: str,
    submit_request: SARSubmitRequest,
    request: Request,
) -> FederalExportResponse:
    """Submit SAR for federal reporting"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="sar_submit",
        resource_type=CJISResourceType.SAR_REPORT,
        resource_id=sar_id,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    report = sar_manager.submit_sar(
        sar_id=sar_id,
        approver_id=user_id,
        approver_name=submit_request.approver_name,
    )

    if not report:
        raise HTTPException(status_code=404, detail="SAR not found")

    validation_errors = None
    if report.validation_result and not report.validation_result.is_valid:
        validation_errors = report.validation_result.errors

    # Mask sensitive data
    masked_data = cjis_compliance_manager.mask_federal_data(report.to_dict())

    return FederalExportResponse(
        success=report.status.value == "submitted",
        export_id=report.id,
        message=f"SAR {report.sar_number} submitted" if report.status.value == "submitted" else "Submission failed",
        data=masked_data,
        validation_errors=validation_errors,
    )


@router.get("/sar/list")
async def list_sars(
    request: Request,
    status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(100, le=1000),
) -> dict[str, Any]:
    """List SARs for agency"""
    user_id, user_name, agency_id = get_user_info(request)

    from app.federal.dhs_sar import SARStatus

    sar_status = None
    if status:
        try:
            sar_status = SARStatus(status)
        except ValueError:
            pass

    reports = sar_manager.get_sars_by_agency(agency_id, sar_status, limit)

    return {
        "success": True,
        "total": len(reports),
        "reports": [
            cjis_compliance_manager.mask_federal_data(r.to_dict())
            for r in reports
        ],
    }


@router.get("/sar/statistics")
async def get_sar_statistics(request: Request) -> dict[str, Any]:
    """Get SAR statistics"""
    user_id, user_name, agency_id = get_user_info(request)
    return sar_manager.get_statistics(agency_id)


# ============================================================================
# CJIS Compliance Endpoints
# ============================================================================

@router.get("/cjis/audit-log")
async def get_cjis_audit_log(
    request: Request,
    action: str | None = Query(None, description="Filter by action"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    since: str | None = Query(None, description="Filter since date (ISO format)"),
    limit: int = Query(100, le=1000),
) -> AuditLogResponse:
    """Get CJIS audit log"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="audit_view",
        resource_type=CJISResourceType.AUDIT_LOG,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    audit_action = None
    if action:
        try:
            audit_action = CJISAuditAction(action)
        except ValueError:
            pass

    audit_resource = None
    if resource_type:
        try:
            audit_resource = CJISResourceType(resource_type)
        except ValueError:
            pass

    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            pass

    entries = cjis_audit_logger.get_audit_log(
        agency_id=agency_id,
        action=audit_action,
        resource_type=audit_resource,
        since=since_dt,
        limit=limit,
    )

    return AuditLogResponse(
        success=True,
        total_entries=len(entries),
        entries=[e.to_dict() for e in entries],
    )


@router.get("/cjis/compliance-report")
async def get_cjis_compliance_report(
    request: Request,
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
) -> ComplianceReportResponse:
    """Generate CJIS compliance report"""
    user_id, user_name, agency_id = get_user_info(request)
    ip_address = get_client_ip(request)

    # Check access
    has_access, error = cjis_compliance_manager.check_federal_access(
        user_id=user_id,
        user_name=user_name,
        agency_id=agency_id,
        operation="audit_view",
        resource_type=CJISResourceType.AUDIT_LOG,
        ip_address=ip_address,
    )

    if not has_access:
        raise HTTPException(status_code=403, detail=error)

    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}") from e

    report = cjis_audit_logger.generate_compliance_report(
        agency_id=agency_id,
        start_date=start_dt,
        end_date=end_dt,
    )

    return ComplianceReportResponse(
        success=True,
        report=report,
    )


@router.get("/cjis/status")
async def get_cjis_compliance_status(request: Request) -> dict[str, Any]:
    """Get CJIS compliance status"""
    return cjis_compliance_manager.get_compliance_status()


# ============================================================================
# Secure Packaging Endpoints
# ============================================================================

@router.get("/secure-packaging/status")
async def get_encryption_status(request: Request) -> dict[str, Any]:
    """Get encryption system status"""
    return secure_packaging_manager.get_encryption_status()


@router.post("/secure-packaging/create")
async def create_secure_package(
    request: Request,
    payload: dict[str, Any],
    message_type: str = Query(..., description="Message type"),
    destination_system: str = Query(..., description="Destination system"),
) -> dict[str, Any]:
    """Create a secure package for federal transmission"""
    user_id, user_name, agency_id = get_user_info(request)

    package = secure_packaging_manager.create_secure_package(
        payload=payload,
        message_type=message_type,
        originating_agency=agency_id,
        destination_system=destination_system,
    )

    return {
        "success": True,
        "package_id": package.id,
        "status": package.status.value,
        "package": package.to_dict(),
    }


# ============================================================================
# Federal Readiness Status Endpoint
# ============================================================================

@router.get("/readiness")
async def get_federal_readiness_status(request: Request) -> dict[str, Any]:
    """Get overall federal readiness status"""
    return {
        "status": "ready",
        "systems": {
            "ndex": {
                "status": "ready",
                "description": "N-DEx data exchange structures implemented",
                "endpoints": [
                    "GET /api/federal/ndex/export/person/{id}",
                    "POST /api/federal/ndex/export/person",
                    "GET /api/federal/ndex/export/incident/{id}",
                    "POST /api/federal/ndex/export/incident",
                ],
            },
            "ncic": {
                "status": "stub_only",
                "description": "NCIC query structure (non-operational stubs)",
                "endpoints": [
                    "POST /api/federal/ncic/query/vehicle",
                    "POST /api/federal/ncic/query/person",
                    "POST /api/federal/ncic/query/gun",
                ],
                "disclaimer": ncic_query_manager.STUB_DISCLAIMER,
            },
            "etrace": {
                "status": "ready",
                "description": "ATF eTrace firearms intelligence export",
                "endpoints": [
                    "GET /api/federal/etrace/export/weapon/{id}",
                    "POST /api/federal/etrace/export/weapon",
                    "GET /api/federal/etrace/export/incident/{id}",
                ],
            },
            "sar": {
                "status": "ready",
                "description": "DHS Suspicious Activity Reporting (ISE-SAR v1.5)",
                "endpoints": [
                    "POST /api/federal/sar/create",
                    "GET /api/federal/sar/{id}",
                    "PUT /api/federal/sar/{id}",
                    "POST /api/federal/sar/{id}/submit",
                ],
            },
        },
        "cjis_compliance": cjis_compliance_manager.get_compliance_status(),
        "encryption": secure_packaging_manager.get_encryption_status(),
        "last_updated": datetime.utcnow().isoformat(),
    }
