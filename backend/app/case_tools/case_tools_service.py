"""
Case Tools Service - Business Logic for Case Management

Provides quick case actions and management tools.
"""

from datetime import datetime, UTC
from typing import List, Optional, Dict
import structlog

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

logger = structlog.get_logger(__name__)


class CaseToolsService:
    """Service for case management shortcuts and rapid tools."""
    
    def __init__(self):
        # In-memory storage for SAFE_MODE operation
        self._notes: Dict[str, CaseNote] = {}
        self._flags: Dict[str, CaseFlag] = {}
        self._unit_requests: Dict[str, UnitRequest] = {}
        self._case_shells: Dict[str, CaseShell] = {}
        self._bolo_zones: Dict[str, BOLOZone] = {}
        self._case_counter = 1000
    
    def _generate_case_number(self) -> str:
        """Generate a unique case number."""
        self._case_counter += 1
        year = datetime.now(UTC).year
        return f"RTCC-{year}-{self._case_counter:05d}"
    
    async def create_note(self, data: CaseNoteCreate, created_by: str) -> CaseNote:
        """Create a case note."""
        import uuid
        case_id = data.case_id or f"TEMP-{uuid.uuid4()}"
        
        note = CaseNote(
            case_id=case_id,
            content=data.content,
            is_rtcc_support=data.is_rtcc_support,
            tags=data.tags,
            created_by=created_by,
        )
        
        self._notes[note.id] = note
        logger.info("case_note_created", note_id=note.id, case_id=case_id, created_by=created_by)
        
        return note
    
    async def get_notes_for_case(self, case_id: str) -> List[CaseNote]:
        """Get all notes for a case."""
        return [n for n in self._notes.values() if n.case_id == case_id]
    
    async def create_flag(self, data: CaseFlagCreate, created_by: str) -> CaseFlag:
        """Flag a case."""
        flag = CaseFlag(
            case_id=data.case_id,
            flag_type=data.flag_type,
            reason=data.reason,
            created_by=created_by,
        )
        
        self._flags[flag.id] = flag
        logger.info("case_flagged", flag_id=flag.id, case_id=data.case_id, flag_type=data.flag_type.value, created_by=created_by)
        
        return flag
    
    async def get_flags_for_case(self, case_id: str) -> List[CaseFlag]:
        """Get all flags for a case."""
        return [f for f in self._flags.values() if f.case_id == case_id and f.is_active]
    
    async def create_unit_request(self, data: UnitRequestCreate, created_by: str) -> UnitRequest:
        """Create a unit follow-up request."""
        request = UnitRequest(
            case_id=data.case_id,
            unit_id=data.unit_id,
            request_type=data.request_type,
            priority=data.priority,
            details=data.details,
            location=data.location,
            created_by=created_by,
        )
        
        self._unit_requests[request.id] = request
        logger.info("unit_request_created", request_id=request.id, case_id=data.case_id, request_type=data.request_type, created_by=created_by)
        
        return request
    
    async def get_pending_unit_requests(self) -> List[UnitRequest]:
        """Get all pending unit requests."""
        return [r for r in self._unit_requests.values() if r.status == "pending"]
    
    async def update_unit_request_status(self, request_id: str, status: str, updated_by: str) -> Optional[UnitRequest]:
        """Update a unit request status."""
        request = self._unit_requests.get(request_id)
        if not request:
            return None
        
        request.status = status
        self._unit_requests[request_id] = request
        logger.info("unit_request_updated", request_id=request_id, status=status, updated_by=updated_by)
        
        return request
    
    async def create_case_shell(self, data: CaseShellCreate, created_by: str) -> CaseShell:
        """Create a case shell (placeholder case)."""
        case_number = self._generate_case_number()
        
        shell = CaseShell(
            case_number=case_number,
            title=data.title,
            description=data.description,
            priority=data.priority,
            incident_type=data.incident_type,
            location=data.location,
            created_by=created_by,
        )
        
        # Add initial note if provided
        if data.initial_notes:
            note = CaseNote(
                case_id=shell.id,
                content=data.initial_notes,
                is_rtcc_support=True,
                created_by=created_by,
            )
            shell.notes.append(note)
            self._notes[note.id] = note
        
        self._case_shells[shell.id] = shell
        logger.info("case_shell_created", case_id=shell.id, case_number=case_number, created_by=created_by)
        
        return shell
    
    async def get_case_shell(self, case_id: str) -> Optional[CaseShell]:
        """Get a case shell by ID."""
        return self._case_shells.get(case_id)
    
    async def get_all_case_shells(self) -> List[CaseShell]:
        """Get all case shells."""
        shells = list(self._case_shells.values())
        shells.sort(key=lambda x: x.created_at, reverse=True)
        return shells
    
    async def create_bolo_zone(self, data: BOLOZoneCreate, created_by: str) -> BOLOZone:
        """Create a BOLO zone."""
        zone = BOLOZone(
            case_id=data.case_id,
            zone_name=data.zone_name,
            description=data.description,
            lat=data.lat,
            lng=data.lng,
            radius_meters=data.radius_meters,
            alert_types=data.alert_types,
            created_by=created_by,
            expires_at=data.expires_at,
        )
        
        self._bolo_zones[zone.id] = zone
        logger.info("bolo_zone_created", zone_id=zone.id, case_id=data.case_id, zone_name=data.zone_name, created_by=created_by)
        
        return zone
    
    async def get_active_bolo_zones(self) -> List[BOLOZone]:
        """Get all active BOLO zones."""
        now = datetime.now(UTC)
        return [
            z for z in self._bolo_zones.values()
            if z.is_active and (z.expires_at is None or z.expires_at > now)
        ]
    
    async def deactivate_bolo_zone(self, zone_id: str, deactivated_by: str) -> Optional[BOLOZone]:
        """Deactivate a BOLO zone."""
        zone = self._bolo_zones.get(zone_id)
        if not zone:
            return None
        
        zone.is_active = False
        self._bolo_zones[zone_id] = zone
        logger.info("bolo_zone_deactivated", zone_id=zone_id, deactivated_by=deactivated_by)
        
        return zone


# Singleton instance for SAFE_MODE operation
_case_tools_service: Optional[CaseToolsService] = None


def get_case_tools_service() -> CaseToolsService:
    """Get the case tools service instance."""
    global _case_tools_service
    if _case_tools_service is None:
        _case_tools_service = CaseToolsService()
    return _case_tools_service
