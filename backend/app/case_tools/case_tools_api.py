"""
Case Tools API - REST Endpoints for Case Management

Provides CJIS-compliant API endpoints for case shortcuts and rapid tools.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from .case_tools_model import (
    CaseNote,
    CaseNoteCreate,
    CaseFlag,
    CaseFlagCreate,
    UnitRequest,
    UnitRequestCreate,
    CaseShell,
    CaseShellCreate,
    BOLOZone,
    BOLOZoneCreate,
)
from .case_tools_service import get_case_tools_service, CaseToolsService

router = APIRouter(prefix="/api/admin/case-tools", tags=["Case Tools"])


def get_current_user() -> str:
    """Get the current user from auth context."""
    return "admin"


@router.post("/note", response_model=CaseNote, status_code=201)
async def create_note(
    data: CaseNoteCreate,
    service: CaseToolsService = Depends(get_case_tools_service),
    user: str = Depends(get_current_user),
):
    """Create a case note."""
    return await service.create_note(data, user)


@router.get("/notes/{case_id}", response_model=List[CaseNote])
async def get_notes_for_case(
    case_id: str,
    service: CaseToolsService = Depends(get_case_tools_service),
):
    """Get all notes for a case."""
    return await service.get_notes_for_case(case_id)


@router.post("/flag", response_model=CaseFlag, status_code=201)
async def flag_case(
    data: CaseFlagCreate,
    service: CaseToolsService = Depends(get_case_tools_service),
    user: str = Depends(get_current_user),
):
    """Flag a case for review or attention."""
    return await service.create_flag(data, user)


@router.get("/flags/{case_id}", response_model=List[CaseFlag])
async def get_flags_for_case(
    case_id: str,
    service: CaseToolsService = Depends(get_case_tools_service),
):
    """Get all flags for a case."""
    return await service.get_flags_for_case(case_id)


@router.post("/request-unit", response_model=UnitRequest, status_code=201)
async def request_unit_followup(
    data: UnitRequestCreate,
    service: CaseToolsService = Depends(get_case_tools_service),
    user: str = Depends(get_current_user),
):
    """Request unit follow-up for a case."""
    return await service.create_unit_request(data, user)


@router.get("/unit-requests/pending", response_model=List[UnitRequest])
async def get_pending_unit_requests(
    service: CaseToolsService = Depends(get_case_tools_service),
):
    """Get all pending unit requests."""
    return await service.get_pending_unit_requests()


@router.patch("/unit-requests/{request_id}/status")
async def update_unit_request_status(
    request_id: str,
    status: str,
    service: CaseToolsService = Depends(get_case_tools_service),
    user: str = Depends(get_current_user),
):
    """Update a unit request status."""
    request = await service.update_unit_request_status(request_id, status, user)
    if not request:
        raise HTTPException(status_code=404, detail="Unit request not found")
    return request


@router.post("/create-shell", response_model=CaseShell, status_code=201)
async def create_case_shell(
    data: CaseShellCreate,
    service: CaseToolsService = Depends(get_case_tools_service),
    user: str = Depends(get_current_user),
):
    """Create a case shell (placeholder case)."""
    return await service.create_case_shell(data, user)


@router.get("/shells", response_model=List[CaseShell])
async def get_all_case_shells(
    service: CaseToolsService = Depends(get_case_tools_service),
):
    """Get all case shells."""
    return await service.get_all_case_shells()


@router.get("/shells/{case_id}", response_model=CaseShell)
async def get_case_shell(
    case_id: str,
    service: CaseToolsService = Depends(get_case_tools_service),
):
    """Get a case shell by ID."""
    shell = await service.get_case_shell(case_id)
    if not shell:
        raise HTTPException(status_code=404, detail="Case shell not found")
    return shell


@router.post("/bolo-zone", response_model=BOLOZone, status_code=201)
async def create_bolo_zone(
    data: BOLOZoneCreate,
    service: CaseToolsService = Depends(get_case_tools_service),
    user: str = Depends(get_current_user),
):
    """Create a BOLO zone for a case."""
    return await service.create_bolo_zone(data, user)


@router.get("/bolo-zones/active", response_model=List[BOLOZone])
async def get_active_bolo_zones(
    service: CaseToolsService = Depends(get_case_tools_service),
):
    """Get all active BOLO zones."""
    return await service.get_active_bolo_zones()


@router.delete("/bolo-zones/{zone_id}", status_code=204)
async def deactivate_bolo_zone(
    zone_id: str,
    service: CaseToolsService = Depends(get_case_tools_service),
    user: str = Depends(get_current_user),
):
    """Deactivate a BOLO zone."""
    zone = await service.deactivate_bolo_zone(zone_id, user)
    if not zone:
        raise HTTPException(status_code=404, detail="BOLO zone not found")
    return None
