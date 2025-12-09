"""
ICS (Incident Command System) Automation for G3TI RTCC-UIP.

Provides automated ICS role assignment, org chart generation,
role-based permissions, and incident-type-specific checklists.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class ICSRole(str, Enum):
    """Standard ICS roles."""

    INCIDENT_COMMANDER = "incident_commander"
    DEPUTY_COMMANDER = "deputy_commander"
    OPERATIONS_CHIEF = "operations_chief"
    PLANNING_CHIEF = "planning_chief"
    LOGISTICS_CHIEF = "logistics_chief"
    FINANCE_CHIEF = "finance_chief"
    INTELLIGENCE_OFFICER = "intelligence_officer"
    SAFETY_OFFICER = "safety_officer"
    PUBLIC_INFO_OFFICER = "public_info_officer"
    LIAISON_OFFICER = "liaison_officer"
    STAGING_MANAGER = "staging_manager"
    DIVISION_SUPERVISOR = "division_supervisor"
    GROUP_SUPERVISOR = "group_supervisor"
    STRIKE_TEAM_LEADER = "strike_team_leader"
    TASK_FORCE_LEADER = "task_force_leader"
    UNIT_LEADER = "unit_leader"
    BRANCH_DIRECTOR = "branch_director"
    MEDICAL_UNIT_LEADER = "medical_unit_leader"
    COMMUNICATIONS_UNIT_LEADER = "communications_unit_leader"
    DOCUMENTATION_UNIT_LEADER = "documentation_unit_leader"


class ICSSection(str, Enum):
    """ICS organizational sections."""

    COMMAND = "command"
    OPERATIONS = "operations"
    PLANNING = "planning"
    LOGISTICS = "logistics"
    FINANCE = "finance"
    INTELLIGENCE = "intelligence"


class RolePermission(str, Enum):
    """Permissions associated with ICS roles."""

    VIEW_ALL = "view_all"
    EDIT_INCIDENT = "edit_incident"
    ASSIGN_RESOURCES = "assign_resources"
    MODIFY_ICS = "modify_ics"
    APPROVE_ACTIONS = "approve_actions"
    SEND_ALERTS = "send_alerts"
    VIEW_INTELLIGENCE = "view_intelligence"
    EDIT_STRATEGY_MAP = "edit_strategy_map"
    MANAGE_COMMUNICATIONS = "manage_communications"
    CREATE_BRIEFINGS = "create_briefings"
    CLOSE_INCIDENT = "close_incident"
    VIEW_SENSITIVE = "view_sensitive"
    MANAGE_AGENCIES = "manage_agencies"


class ICSRoleAssignment(BaseModel):
    """Assignment of a person to an ICS role."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    role: ICSRole
    section: ICSSection
    badge: str
    name: str | None = None
    agency: str | None = None
    contact: str | None = None
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    assigned_by: str | None = None
    relieved_at: datetime | None = None
    relieved_by: str | None = None
    is_active: bool = True
    notes: str | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-ICS-{uuid.uuid4().hex[:12].upper()}")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class ICSChecklistItem(BaseModel):
    """Checklist item for ICS role."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: ICSRole
    description: str
    is_required: bool = True
    completed: bool = False
    completed_at: datetime | None = None
    completed_by: str | None = None
    notes: str | None = None


class ICSRoleDefinition(BaseModel):
    """Definition of an ICS role with permissions and responsibilities."""

    role: ICSRole
    section: ICSSection
    title: str
    description: str
    permissions: list[RolePermission]
    reports_to: ICSRole | None = None
    checklist: list[str] = Field(default_factory=list)


class ICSOrgChart(BaseModel):
    """ICS organizational chart for an incident."""

    incident_id: str
    assignments: list[ICSRoleAssignment] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def get_by_role(self, role: ICSRole) -> ICSRoleAssignment | None:
        """Get assignment by role."""
        role_value = role.value if isinstance(role, ICSRole) else role
        for assignment in self.assignments:
            if assignment.role == role_value and assignment.is_active:
                return assignment
        return None

    def get_by_section(self, section: ICSSection) -> list[ICSRoleAssignment]:
        """Get all assignments in a section."""
        section_value = section.value if isinstance(section, ICSSection) else section
        return [a for a in self.assignments if a.section == section_value and a.is_active]


class ICSEvent(BaseModel):
    """Event related to ICS changes."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    event_type: str
    role: ICSRole | None = None
    badge: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    user_id: str | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-ICSE-{uuid.uuid4().hex[:12].upper()}")


class ICSManager:
    """
    Manager for ICS (Incident Command System) operations.

    Provides role assignment, org chart generation, permissions
    management, and checklist tracking for incident command.
    """

    def __init__(self) -> None:
        """Initialize the ICS manager."""
        self._assignments: dict[str, list[ICSRoleAssignment]] = {}  # incident_id -> assignments
        self._events: list[ICSEvent] = []
        self._checklists: dict[str, list[ICSChecklistItem]] = {}  # incident_id -> checklist items
        self._role_definitions = self._init_role_definitions()
        self._role_permissions = self._init_role_permissions()

        logger.info("ics_manager_initialized")

    def _init_role_definitions(self) -> dict[ICSRole, ICSRoleDefinition]:
        """Initialize role definitions."""
        return {
            ICSRole.INCIDENT_COMMANDER: ICSRoleDefinition(
                role=ICSRole.INCIDENT_COMMANDER,
                section=ICSSection.COMMAND,
                title="Incident Commander",
                description="Overall incident management and authority",
                permissions=[
                    RolePermission.VIEW_ALL,
                    RolePermission.EDIT_INCIDENT,
                    RolePermission.ASSIGN_RESOURCES,
                    RolePermission.MODIFY_ICS,
                    RolePermission.APPROVE_ACTIONS,
                    RolePermission.SEND_ALERTS,
                    RolePermission.VIEW_INTELLIGENCE,
                    RolePermission.EDIT_STRATEGY_MAP,
                    RolePermission.MANAGE_COMMUNICATIONS,
                    RolePermission.CREATE_BRIEFINGS,
                    RolePermission.CLOSE_INCIDENT,
                    RolePermission.VIEW_SENSITIVE,
                    RolePermission.MANAGE_AGENCIES,
                ],
                reports_to=None,
                checklist=[
                    "Assume command and establish command post",
                    "Assess situation and establish priorities",
                    "Determine incident objectives",
                    "Establish ICS organization",
                    "Ensure planning meetings are scheduled",
                    "Approve and authorize implementation of IAP",
                    "Ensure adequate safety measures are in place",
                    "Coordinate with agency administrators",
                    "Approve requests for additional resources",
                    "Authorize release of information",
                ],
            ),
            ICSRole.DEPUTY_COMMANDER: ICSRoleDefinition(
                role=ICSRole.DEPUTY_COMMANDER,
                section=ICSSection.COMMAND,
                title="Deputy Incident Commander",
                description="Assists IC and assumes command in IC absence",
                permissions=[
                    RolePermission.VIEW_ALL,
                    RolePermission.EDIT_INCIDENT,
                    RolePermission.ASSIGN_RESOURCES,
                    RolePermission.APPROVE_ACTIONS,
                    RolePermission.SEND_ALERTS,
                    RolePermission.VIEW_INTELLIGENCE,
                    RolePermission.CREATE_BRIEFINGS,
                    RolePermission.VIEW_SENSITIVE,
                ],
                reports_to=ICSRole.INCIDENT_COMMANDER,
                checklist=[
                    "Obtain briefing from IC",
                    "Assist IC as directed",
                    "Be prepared to assume IC role",
                    "Coordinate with section chiefs",
                ],
            ),
            ICSRole.OPERATIONS_CHIEF: ICSRoleDefinition(
                role=ICSRole.OPERATIONS_CHIEF,
                section=ICSSection.OPERATIONS,
                title="Operations Section Chief",
                description="Manages tactical operations",
                permissions=[
                    RolePermission.VIEW_ALL,
                    RolePermission.ASSIGN_RESOURCES,
                    RolePermission.SEND_ALERTS,
                    RolePermission.VIEW_INTELLIGENCE,
                    RolePermission.EDIT_STRATEGY_MAP,
                ],
                reports_to=ICSRole.INCIDENT_COMMANDER,
                checklist=[
                    "Obtain briefing from IC",
                    "Develop operations portion of IAP",
                    "Brief and assign operations personnel",
                    "Supervise operations",
                    "Determine need for additional resources",
                    "Review suggested resource assignments",
                    "Report information about special activities",
                    "Approve release of resources",
                ],
            ),
            ICSRole.PLANNING_CHIEF: ICSRoleDefinition(
                role=ICSRole.PLANNING_CHIEF,
                section=ICSSection.PLANNING,
                title="Planning Section Chief",
                description="Manages planning and documentation",
                permissions=[
                    RolePermission.VIEW_ALL,
                    RolePermission.VIEW_INTELLIGENCE,
                    RolePermission.CREATE_BRIEFINGS,
                ],
                reports_to=ICSRole.INCIDENT_COMMANDER,
                checklist=[
                    "Obtain briefing from IC",
                    "Activate planning section units",
                    "Establish information requirements",
                    "Conduct planning meetings",
                    "Prepare IAP",
                    "Track resources",
                    "Compile and display incident status",
                    "Prepare demobilization plan",
                ],
            ),
            ICSRole.LOGISTICS_CHIEF: ICSRoleDefinition(
                role=ICSRole.LOGISTICS_CHIEF,
                section=ICSSection.LOGISTICS,
                title="Logistics Section Chief",
                description="Manages resources and support",
                permissions=[
                    RolePermission.VIEW_ALL,
                    RolePermission.ASSIGN_RESOURCES,
                ],
                reports_to=ICSRole.INCIDENT_COMMANDER,
                checklist=[
                    "Obtain briefing from IC",
                    "Plan organization of logistics section",
                    "Assign work locations and tasks",
                    "Notify resources unit of logistics section units",
                    "Assemble and brief branch directors",
                    "Identify anticipated and known incident needs",
                    "Provide input to IAP",
                    "Review IAP and estimate logistics needs",
                ],
            ),
            ICSRole.FINANCE_CHIEF: ICSRoleDefinition(
                role=ICSRole.FINANCE_CHIEF,
                section=ICSSection.FINANCE,
                title="Finance/Admin Section Chief",
                description="Manages financial and administrative functions",
                permissions=[
                    RolePermission.VIEW_ALL,
                ],
                reports_to=ICSRole.INCIDENT_COMMANDER,
                checklist=[
                    "Obtain briefing from IC",
                    "Attend planning meetings",
                    "Manage financial aspects of incident",
                    "Provide financial input to IAP",
                    "Ensure all personnel time is recorded",
                    "Ensure all equipment use is recorded",
                    "Process claims",
                    "Prepare incident cost analysis",
                ],
            ),
            ICSRole.INTELLIGENCE_OFFICER: ICSRoleDefinition(
                role=ICSRole.INTELLIGENCE_OFFICER,
                section=ICSSection.INTELLIGENCE,
                title="Intelligence/Investigations Officer",
                description="Manages intelligence gathering and analysis (RTCC)",
                permissions=[
                    RolePermission.VIEW_ALL,
                    RolePermission.VIEW_INTELLIGENCE,
                    RolePermission.SEND_ALERTS,
                    RolePermission.CREATE_BRIEFINGS,
                    RolePermission.VIEW_SENSITIVE,
                ],
                reports_to=ICSRole.INCIDENT_COMMANDER,
                checklist=[
                    "Obtain briefing from IC",
                    "Establish intelligence collection plan",
                    "Coordinate with RTCC",
                    "Analyze incoming intelligence",
                    "Prepare intelligence briefings",
                    "Disseminate intelligence products",
                    "Coordinate with other agencies",
                    "Maintain intelligence files",
                ],
            ),
            ICSRole.SAFETY_OFFICER: ICSRoleDefinition(
                role=ICSRole.SAFETY_OFFICER,
                section=ICSSection.COMMAND,
                title="Safety Officer",
                description="Monitors safety conditions and develops safety measures",
                permissions=[
                    RolePermission.VIEW_ALL,
                    RolePermission.SEND_ALERTS,
                    RolePermission.VIEW_INTELLIGENCE,
                ],
                reports_to=ICSRole.INCIDENT_COMMANDER,
                checklist=[
                    "Obtain briefing from IC",
                    "Identify hazardous situations",
                    "Participate in planning meetings",
                    "Review IAP for safety implications",
                    "Exercise emergency authority to stop unsafe acts",
                    "Investigate accidents",
                    "Review and approve medical plan",
                    "Ensure safety message is included in IAP",
                ],
            ),
            ICSRole.PUBLIC_INFO_OFFICER: ICSRoleDefinition(
                role=ICSRole.PUBLIC_INFO_OFFICER,
                section=ICSSection.COMMAND,
                title="Public Information Officer",
                description="Manages public information and media relations",
                permissions=[
                    RolePermission.VIEW_ALL,
                    RolePermission.CREATE_BRIEFINGS,
                ],
                reports_to=ICSRole.INCIDENT_COMMANDER,
                checklist=[
                    "Obtain briefing from IC",
                    "Establish media information center",
                    "Prepare initial information summary",
                    "Arrange for tours and interviews",
                    "Obtain IC approval for releases",
                    "Release information to media",
                    "Attend planning meetings",
                    "Respond to special requests",
                ],
            ),
            ICSRole.LIAISON_OFFICER: ICSRoleDefinition(
                role=ICSRole.LIAISON_OFFICER,
                section=ICSSection.COMMAND,
                title="Liaison Officer",
                description="Coordinates with assisting and cooperating agencies",
                permissions=[
                    RolePermission.VIEW_ALL,
                    RolePermission.MANAGE_AGENCIES,
                ],
                reports_to=ICSRole.INCIDENT_COMMANDER,
                checklist=[
                    "Obtain briefing from IC",
                    "Provide point of contact for agency representatives",
                    "Identify agency representatives",
                    "Respond to requests from incident personnel",
                    "Monitor incident operations",
                    "Attend planning meetings",
                    "Keep agencies informed of incident status",
                ],
            ),
            ICSRole.STAGING_MANAGER: ICSRoleDefinition(
                role=ICSRole.STAGING_MANAGER,
                section=ICSSection.OPERATIONS,
                title="Staging Area Manager",
                description="Manages staging area operations",
                permissions=[
                    RolePermission.VIEW_ALL,
                    RolePermission.ASSIGN_RESOURCES,
                ],
                reports_to=ICSRole.OPERATIONS_CHIEF,
                checklist=[
                    "Obtain briefing from Operations Chief",
                    "Establish staging area layout",
                    "Determine support needs",
                    "Establish check-in function",
                    "Post areas for identification",
                    "Request maintenance service",
                    "Respond to requests for resources",
                    "Maintain staging area status",
                ],
            ),
        }

    def _init_role_permissions(self) -> dict[ICSRole, list[RolePermission]]:
        """Get permissions for each role."""
        return {
            role: definition.permissions
            for role, definition in self._role_definitions.items()
        }

    def get_role_definition(self, role: ICSRole) -> ICSRoleDefinition | None:
        """Get definition for a role."""
        return self._role_definitions.get(role)

    def get_role_permissions(self, role: ICSRole) -> list[RolePermission]:
        """Get permissions for a role."""
        return self._role_permissions.get(role, [])

    def get_section_for_role(self, role: ICSRole) -> ICSSection:
        """Get the section a role belongs to."""
        definition = self._role_definitions.get(role)
        if definition:
            return definition.section
        return ICSSection.COMMAND

    async def assign_role(
        self,
        incident_id: str,
        role: ICSRole,
        badge: str,
        name: str | None = None,
        agency: str | None = None,
        contact: str | None = None,
        assigned_by: str | None = None,
        notes: str | None = None,
    ) -> ICSRoleAssignment:
        """
        Assign a person to an ICS role.

        Args:
            incident_id: ID of the incident
            role: ICS role to assign
            badge: Badge number of assignee
            name: Name of assignee
            agency: Agency of assignee
            contact: Contact information
            assigned_by: User making assignment
            notes: Assignment notes

        Returns:
            ICSRoleAssignment
        """
        # Get section for role
        section = self.get_section_for_role(role)

        # Check if role is already assigned
        existing = await self.get_role_assignment(incident_id, role)
        if existing and existing.is_active:
            # Relieve existing assignment
            await self.relieve_role(
                incident_id=incident_id,
                role=role,
                relieved_by=assigned_by,
                notes=f"Relieved for reassignment to {badge}",
            )

        assignment = ICSRoleAssignment(
            incident_id=incident_id,
            role=role,
            section=section,
            badge=badge,
            name=name,
            agency=agency,
            contact=contact,
            assigned_by=assigned_by,
            notes=notes,
        )

        if incident_id not in self._assignments:
            self._assignments[incident_id] = []
        self._assignments[incident_id].append(assignment)

        # Initialize checklist for role
        await self._init_role_checklist(incident_id, role, badge)

        # Log event
        event = ICSEvent(
            incident_id=incident_id,
            event_type="ics_role_assigned",
            role=role,
            badge=badge,
            data={
                "name": name,
                "agency": agency,
                "section": section.value if isinstance(section, ICSSection) else section,
            },
            user_id=assigned_by,
        )
        self._events.append(event)

        logger.info(
            "ics_role_assigned",
            incident_id=incident_id,
            role=role,
            badge=badge,
            assigned_by=assigned_by,
            audit_id=assignment.audit_id,
        )

        return assignment

    async def reassign_role(
        self,
        incident_id: str,
        role: ICSRole,
        new_badge: str,
        new_name: str | None = None,
        new_agency: str | None = None,
        reassigned_by: str | None = None,
        notes: str | None = None,
    ) -> ICSRoleAssignment:
        """
        Reassign an ICS role to a different person.

        Args:
            incident_id: ID of the incident
            role: ICS role to reassign
            new_badge: Badge of new assignee
            new_name: Name of new assignee
            new_agency: Agency of new assignee
            reassigned_by: User making reassignment
            notes: Reassignment notes

        Returns:
            New ICSRoleAssignment
        """
        # Relieve current assignment
        await self.relieve_role(
            incident_id=incident_id,
            role=role,
            relieved_by=reassigned_by,
            notes=notes or f"Reassigned to {new_badge}",
        )

        # Create new assignment
        return await self.assign_role(
            incident_id=incident_id,
            role=role,
            badge=new_badge,
            name=new_name,
            agency=new_agency,
            assigned_by=reassigned_by,
            notes=notes,
        )

    async def relieve_role(
        self,
        incident_id: str,
        role: ICSRole,
        relieved_by: str | None = None,
        notes: str | None = None,
    ) -> ICSRoleAssignment | None:
        """
        Relieve a person from an ICS role.

        Args:
            incident_id: ID of the incident
            role: ICS role to relieve
            relieved_by: User relieving the role
            notes: Relief notes

        Returns:
            Relieved ICSRoleAssignment or None
        """
        assignment = await self.get_role_assignment(incident_id, role)
        if not assignment or not assignment.is_active:
            return None

        assignment.is_active = False
        assignment.relieved_at = datetime.now(UTC)
        assignment.relieved_by = relieved_by
        if notes:
            assignment.notes = (assignment.notes or "") + f" | Relieved: {notes}"

        # Log event
        event = ICSEvent(
            incident_id=incident_id,
            event_type="ics_role_relieved",
            role=role,
            badge=assignment.badge,
            data={"notes": notes},
            user_id=relieved_by,
        )
        self._events.append(event)

        logger.info(
            "ics_role_relieved",
            incident_id=incident_id,
            role=role,
            badge=assignment.badge,
            relieved_by=relieved_by,
            audit_id=assignment.audit_id,
        )

        return assignment

    async def get_role_assignment(
        self,
        incident_id: str,
        role: ICSRole,
        active_only: bool = True,
    ) -> ICSRoleAssignment | None:
        """
        Get current assignment for a role.

        Args:
            incident_id: ID of the incident
            role: ICS role to look up
            active_only: Only return active assignments

        Returns:
            ICSRoleAssignment or None
        """
        assignments = self._assignments.get(incident_id, [])
        role_value = role.value if isinstance(role, ICSRole) else role

        for assignment in reversed(assignments):  # Most recent first
            if assignment.role == role_value:
                if active_only and not assignment.is_active:
                    continue
                return assignment
        return None

    async def get_assignments_for_badge(
        self,
        incident_id: str,
        badge: str,
        active_only: bool = True,
    ) -> list[ICSRoleAssignment]:
        """
        Get all role assignments for a badge.

        Args:
            incident_id: ID of the incident
            badge: Badge number
            active_only: Only return active assignments

        Returns:
            List of ICSRoleAssignment
        """
        assignments = self._assignments.get(incident_id, [])
        result = [a for a in assignments if a.badge == badge]
        if active_only:
            result = [a for a in result if a.is_active]
        return result

    async def get_org_chart(self, incident_id: str) -> ICSOrgChart:
        """
        Generate ICS organizational chart for incident.

        Args:
            incident_id: ID of the incident

        Returns:
            ICSOrgChart
        """
        assignments = self._assignments.get(incident_id, [])
        active_assignments = [a for a in assignments if a.is_active]

        return ICSOrgChart(
            incident_id=incident_id,
            assignments=active_assignments,
        )

    async def get_section_assignments(
        self,
        incident_id: str,
        section: ICSSection,
    ) -> list[ICSRoleAssignment]:
        """
        Get all assignments in a section.

        Args:
            incident_id: ID of the incident
            section: ICS section

        Returns:
            List of ICSRoleAssignment
        """
        assignments = self._assignments.get(incident_id, [])
        section_value = section.value if isinstance(section, ICSSection) else section
        return [a for a in assignments if a.section == section_value and a.is_active]

    async def _init_role_checklist(
        self,
        incident_id: str,
        role: ICSRole,
        badge: str,
    ) -> list[ICSChecklistItem]:
        """Initialize checklist for a role assignment."""
        definition = self._role_definitions.get(role)
        if not definition:
            return []

        checklist_key = f"{incident_id}:{role.value if isinstance(role, ICSRole) else role}:{badge}"
        items = []

        for item_text in definition.checklist:
            item = ICSChecklistItem(
                role=role,
                description=item_text,
            )
            items.append(item)

        self._checklists[checklist_key] = items
        return items

    async def get_role_checklist(
        self,
        incident_id: str,
        role: ICSRole,
        badge: str,
    ) -> list[ICSChecklistItem]:
        """
        Get checklist for a role assignment.

        Args:
            incident_id: ID of the incident
            role: ICS role
            badge: Badge of assignee

        Returns:
            List of ICSChecklistItem
        """
        checklist_key = f"{incident_id}:{role.value if isinstance(role, ICSRole) else role}:{badge}"
        return self._checklists.get(checklist_key, [])

    async def complete_checklist_item(
        self,
        incident_id: str,
        role: ICSRole,
        badge: str,
        item_id: str,
        completed_by: str | None = None,
        notes: str | None = None,
    ) -> ICSChecklistItem | None:
        """
        Mark a checklist item as completed.

        Args:
            incident_id: ID of the incident
            role: ICS role
            badge: Badge of assignee
            item_id: ID of checklist item
            completed_by: User completing item
            notes: Completion notes

        Returns:
            Updated ICSChecklistItem or None
        """
        checklist_key = f"{incident_id}:{role.value if isinstance(role, ICSRole) else role}:{badge}"
        items = self._checklists.get(checklist_key, [])

        for item in items:
            if item.id == item_id:
                item.completed = True
                item.completed_at = datetime.now(UTC)
                item.completed_by = completed_by
                item.notes = notes

                logger.info(
                    "ics_checklist_item_completed",
                    incident_id=incident_id,
                    role=role,
                    item_id=item_id,
                    completed_by=completed_by,
                )

                return item

        return None

    async def get_all_checklists(
        self,
        incident_id: str,
    ) -> dict[str, list[ICSChecklistItem]]:
        """
        Get all checklists for an incident.

        Args:
            incident_id: ID of the incident

        Returns:
            Dictionary of role:badge -> checklist items
        """
        result = {}
        for key, items in self._checklists.items():
            if key.startswith(f"{incident_id}:"):
                result[key] = items
        return result

    def has_permission(
        self,
        incident_id: str,
        badge: str,
        permission: RolePermission,
    ) -> bool:
        """
        Check if a badge has a specific permission for an incident.

        Args:
            incident_id: ID of the incident
            badge: Badge number
            permission: Permission to check

        Returns:
            True if badge has permission
        """
        assignments = self._assignments.get(incident_id, [])
        permission_value = permission.value if isinstance(permission, RolePermission) else permission

        for assignment in assignments:
            if assignment.badge == badge and assignment.is_active:
                role = ICSRole(assignment.role) if isinstance(assignment.role, str) else assignment.role
                role_perms = self.get_role_permissions(role)
                if permission in role_perms or RolePermission(permission_value) in role_perms:
                    return True

        return False

    async def get_events(
        self,
        incident_id: str,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[ICSEvent]:
        """
        Get ICS events for an incident.

        Args:
            incident_id: ID of the incident
            event_type: Filter by event type
            limit: Maximum number to return

        Returns:
            List of ICSEvent
        """
        events = [e for e in self._events if e.incident_id == incident_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]

    async def get_incident_statistics(self, incident_id: str) -> dict[str, Any]:
        """
        Get ICS statistics for an incident.

        Args:
            incident_id: ID of the incident

        Returns:
            Dictionary of statistics
        """
        assignments = self._assignments.get(incident_id, [])
        active_assignments = [a for a in assignments if a.is_active]

        # Count by section
        by_section: dict[str, int] = {}
        for assignment in active_assignments:
            section = assignment.section
            by_section[section] = by_section.get(section, 0) + 1

        # Count by agency
        by_agency: dict[str, int] = {}
        for assignment in active_assignments:
            agency = assignment.agency or "Unknown"
            by_agency[agency] = by_agency.get(agency, 0) + 1

        # Checklist completion
        total_items = 0
        completed_items = 0
        for key, items in self._checklists.items():
            if key.startswith(f"{incident_id}:"):
                total_items += len(items)
                completed_items += sum(1 for i in items if i.completed)

        return {
            "total_assignments": len(active_assignments),
            "total_historical": len(assignments),
            "by_section": by_section,
            "by_agency": by_agency,
            "checklist_total": total_items,
            "checklist_completed": completed_items,
            "checklist_percentage": (completed_items / total_items * 100) if total_items > 0 else 0,
        }
