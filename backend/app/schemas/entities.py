"""
Entity schemas for the G3TI RTCC-UIP Backend.

This module defines schemas for all graph entities stored in Neo4j:
- Person: Individuals involved in incidents or investigations
- Vehicle: Vehicles associated with incidents or persons
- Incident: Crime incidents and events
- Weapon: Weapons involved in incidents
- ShellCasing: Ballistic evidence
- Address: Geographic locations
- Camera: Surveillance cameras
- LicensePlate: License plate records
- Association: Relationships between entities
"""

from datetime import date, datetime
from enum import Enum

from pydantic import Field

from app.schemas.common import GeoLocation, RTCCBaseModel, TimestampMixin

# Enums for entity types and statuses


class Gender(str, Enum):
    """Gender enumeration."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class IncidentType(str, Enum):
    """Types of incidents."""

    SHOOTING = "shooting"
    ROBBERY = "robbery"
    ASSAULT = "assault"
    BURGLARY = "burglary"
    THEFT = "theft"
    HOMICIDE = "homicide"
    DRUG_OFFENSE = "drug_offense"
    TRAFFIC = "traffic"
    DOMESTIC = "domestic"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    OTHER = "other"


class IncidentStatus(str, Enum):
    """Incident status values."""

    ACTIVE = "active"
    UNDER_INVESTIGATION = "under_investigation"
    CLOSED = "closed"
    COLD_CASE = "cold_case"


class VehicleType(str, Enum):
    """Vehicle type enumeration."""

    SEDAN = "sedan"
    SUV = "suv"
    TRUCK = "truck"
    VAN = "van"
    MOTORCYCLE = "motorcycle"
    OTHER = "other"


class CameraStatus(str, Enum):
    """Camera status values."""

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class AssociationType(str, Enum):
    """Types of associations between entities."""

    SUSPECT = "suspect"
    VICTIM = "victim"
    WITNESS = "witness"
    OWNER = "owner"
    DRIVER = "driver"
    PASSENGER = "passenger"
    RESIDENT = "resident"
    ASSOCIATE = "associate"
    FAMILY = "family"
    EMPLOYER = "employer"
    EMPLOYEE = "employee"


# Person Schemas


class PersonBase(RTCCBaseModel):
    """Base schema for Person entity."""

    first_name: str = Field(min_length=1, max_length=100, description="First name")
    last_name: str = Field(min_length=1, max_length=100, description="Last name")
    middle_name: str | None = Field(default=None, max_length=100, description="Middle name")
    aliases: list[str] = Field(default_factory=list, description="Known aliases")
    date_of_birth: date | None = Field(default=None, description="Date of birth")
    gender: Gender = Field(default=Gender.UNKNOWN, description="Gender")
    race: str | None = Field(default=None, max_length=50, description="Race/ethnicity")
    height_inches: int | None = Field(default=None, ge=0, le=120, description="Height in inches")
    weight_lbs: int | None = Field(default=None, ge=0, le=1000, description="Weight in pounds")
    hair_color: str | None = Field(default=None, max_length=50, description="Hair color")
    eye_color: str | None = Field(default=None, max_length=50, description="Eye color")
    distinguishing_marks: str | None = Field(
        default=None, max_length=500, description="Tattoos, scars, or other distinguishing marks"
    )
    ssn_last_four: str | None = Field(
        default=None, pattern=r"^\d{4}$", description="Last 4 digits of SSN"
    )
    drivers_license: str | None = Field(
        default=None, max_length=50, description="Driver's license number"
    )
    phone_numbers: list[str] = Field(default_factory=list, description="Known phone numbers")
    email_addresses: list[str] = Field(default_factory=list, description="Known email addresses")
    gang_affiliation: str | None = Field(
        default=None, max_length=100, description="Known gang affiliation"
    )
    is_armed_dangerous: bool = Field(default=False, description="Armed and dangerous flag")
    notes: str | None = Field(default=None, max_length=2000, description="Additional notes")


class PersonCreate(PersonBase):
    """Schema for creating a Person entity."""

    pass


class PersonUpdate(RTCCBaseModel):
    """Schema for updating a Person entity."""

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    middle_name: str | None = None
    aliases: list[str] | None = None
    date_of_birth: date | None = None
    gender: Gender | None = None
    race: str | None = None
    height_inches: int | None = None
    weight_lbs: int | None = None
    hair_color: str | None = None
    eye_color: str | None = None
    distinguishing_marks: str | None = None
    phone_numbers: list[str] | None = None
    email_addresses: list[str] | None = None
    gang_affiliation: str | None = None
    is_armed_dangerous: bool | None = None
    notes: str | None = None


class PersonResponse(PersonBase, TimestampMixin):
    """Schema for Person entity response."""

    id: str = Field(description="Unique person identifier")
    full_name: str = Field(description="Full name")
    age: int | None = Field(default=None, description="Calculated age")
    incident_count: int = Field(default=0, description="Number of associated incidents")

    @property
    def display_name(self) -> str:
        """Get display name with aliases."""
        name = f"{self.last_name}, {self.first_name}"
        if self.aliases:
            name += f" (AKA: {', '.join(self.aliases[:3])})"
        return name


# Vehicle Schemas


class VehicleBase(RTCCBaseModel):
    """Base schema for Vehicle entity."""

    license_plate: str = Field(max_length=20, description="License plate number")
    plate_state: str = Field(max_length=2, description="License plate state")
    make: str | None = Field(default=None, max_length=50, description="Vehicle make")
    model: str | None = Field(default=None, max_length=50, description="Vehicle model")
    year: int | None = Field(default=None, ge=1900, le=2100, description="Vehicle year")
    color: str | None = Field(default=None, max_length=50, description="Vehicle color")
    vehicle_type: VehicleType = Field(default=VehicleType.OTHER, description="Vehicle type")
    vin: str | None = Field(
        default=None, max_length=17, description="Vehicle identification number"
    )
    is_stolen: bool = Field(default=False, description="Stolen vehicle flag")
    is_wanted: bool = Field(default=False, description="Wanted vehicle flag")
    notes: str | None = Field(default=None, max_length=1000, description="Additional notes")


class VehicleCreate(VehicleBase):
    """Schema for creating a Vehicle entity."""

    pass


class VehicleUpdate(RTCCBaseModel):
    """Schema for updating a Vehicle entity."""

    license_plate: str | None = Field(default=None, max_length=20)
    plate_state: str | None = Field(default=None, max_length=2)
    make: str | None = None
    model: str | None = None
    year: int | None = None
    color: str | None = None
    vehicle_type: VehicleType | None = None
    vin: str | None = None
    is_stolen: bool | None = None
    is_wanted: bool | None = None
    notes: str | None = None


class VehicleResponse(VehicleBase, TimestampMixin):
    """Schema for Vehicle entity response."""

    id: str = Field(description="Unique vehicle identifier")
    sighting_count: int = Field(default=0, description="Number of sightings")
    last_seen_at: datetime | None = Field(default=None, description="Last sighting timestamp")
    last_seen_location: GeoLocation | None = Field(default=None, description="Last known location")

    @property
    def display_name(self) -> str:
        """Get display name for vehicle."""
        parts = []
        if self.year:
            parts.append(str(self.year))
        if self.color:
            parts.append(self.color)
        if self.make:
            parts.append(self.make)
        if self.model:
            parts.append(self.model)
        return " ".join(parts) or f"Vehicle {self.license_plate}"


# Incident Schemas


class IncidentBase(RTCCBaseModel):
    """Base schema for Incident entity."""

    incident_number: str = Field(max_length=50, description="Incident/case number")
    incident_type: IncidentType = Field(description="Type of incident")
    title: str = Field(max_length=200, description="Incident title/summary")
    description: str | None = Field(
        default=None, max_length=5000, description="Detailed description"
    )
    occurred_at: datetime = Field(description="When the incident occurred")
    reported_at: datetime = Field(description="When the incident was reported")
    location: GeoLocation | None = Field(default=None, description="Incident location")
    address: str | None = Field(default=None, max_length=500, description="Incident address")
    status: IncidentStatus = Field(default=IncidentStatus.ACTIVE, description="Incident status")
    severity: int = Field(default=1, ge=1, le=5, description="Severity level (1-5)")
    responding_units: list[str] = Field(default_factory=list, description="Responding unit IDs")
    is_priority: bool = Field(default=False, description="Priority incident flag")


class IncidentCreate(IncidentBase):
    """Schema for creating an Incident entity."""

    pass


class IncidentUpdate(RTCCBaseModel):
    """Schema for updating an Incident entity."""

    incident_type: IncidentType | None = None
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    occurred_at: datetime | None = None
    location: GeoLocation | None = None
    address: str | None = None
    status: IncidentStatus | None = None
    severity: int | None = Field(default=None, ge=1, le=5)
    responding_units: list[str] | None = None
    is_priority: bool | None = None


class IncidentResponse(IncidentBase, TimestampMixin):
    """Schema for Incident entity response."""

    id: str = Field(description="Unique incident identifier")
    person_count: int = Field(default=0, description="Number of associated persons")
    vehicle_count: int = Field(default=0, description="Number of associated vehicles")
    evidence_count: int = Field(default=0, description="Number of evidence items")


# Weapon Schemas


class WeaponBase(RTCCBaseModel):
    """Base schema for Weapon entity."""

    weapon_type: str = Field(max_length=50, description="Type of weapon")
    make: str | None = Field(default=None, max_length=50, description="Weapon make")
    model: str | None = Field(default=None, max_length=50, description="Weapon model")
    caliber: str | None = Field(default=None, max_length=20, description="Caliber")
    serial_number: str | None = Field(default=None, max_length=50, description="Serial number")
    is_stolen: bool = Field(default=False, description="Stolen weapon flag")
    is_recovered: bool = Field(default=False, description="Recovered weapon flag")
    recovery_location: str | None = Field(
        default=None, max_length=500, description="Recovery location"
    )
    recovery_date: datetime | None = Field(default=None, description="Recovery date")
    notes: str | None = Field(default=None, max_length=1000, description="Additional notes")


class WeaponCreate(WeaponBase):
    """Schema for creating a Weapon entity."""

    pass


class WeaponResponse(WeaponBase, TimestampMixin):
    """Schema for Weapon entity response."""

    id: str = Field(description="Unique weapon identifier")
    incident_count: int = Field(default=0, description="Number of associated incidents")


# Shell Casing Schemas


class ShellCasingBase(RTCCBaseModel):
    """Base schema for ShellCasing entity."""

    caliber: str = Field(max_length=20, description="Caliber")
    headstamp: str | None = Field(default=None, max_length=50, description="Headstamp markings")
    collection_location: GeoLocation | None = Field(default=None, description="Collection location")
    collection_address: str | None = Field(
        default=None, max_length=500, description="Collection address"
    )
    collection_date: datetime = Field(description="Collection date/time")
    nibin_hit: bool = Field(default=False, description="NIBIN hit flag")
    nibin_correlation_id: str | None = Field(
        default=None, max_length=50, description="NIBIN correlation ID"
    )
    notes: str | None = Field(default=None, max_length=1000, description="Additional notes")


class ShellCasingCreate(ShellCasingBase):
    """Schema for creating a ShellCasing entity."""

    pass


class ShellCasingResponse(ShellCasingBase, TimestampMixin):
    """Schema for ShellCasing entity response."""

    id: str = Field(description="Unique shell casing identifier")
    linked_casings: list[str] = Field(
        default_factory=list, description="IDs of linked shell casings"
    )


# Address Schemas


class AddressBase(RTCCBaseModel):
    """Base schema for Address entity."""

    street_address: str = Field(max_length=200, description="Street address")
    unit: str | None = Field(default=None, max_length=50, description="Unit/apartment number")
    city: str = Field(max_length=100, description="City")
    state: str = Field(max_length=2, description="State code")
    zip_code: str = Field(max_length=10, description="ZIP code")
    location: GeoLocation | None = Field(default=None, description="Geocoded location")
    address_type: str | None = Field(
        default=None, max_length=50, description="Address type (residential, commercial, etc.)"
    )
    is_hotspot: bool = Field(default=False, description="Crime hotspot flag")
    notes: str | None = Field(default=None, max_length=1000, description="Additional notes")


class AddressCreate(AddressBase):
    """Schema for creating an Address entity."""

    pass


class AddressResponse(AddressBase, TimestampMixin):
    """Schema for Address entity response."""

    id: str = Field(description="Unique address identifier")
    incident_count: int = Field(default=0, description="Number of incidents at this address")

    @property
    def full_address(self) -> str:
        """Get full formatted address."""
        parts = [self.street_address]
        if self.unit:
            parts.append(f"Unit {self.unit}")
        parts.append(f"{self.city}, {self.state} {self.zip_code}")
        return ", ".join(parts)


# Camera Schemas


class CameraBase(RTCCBaseModel):
    """Base schema for Camera entity."""

    camera_id: str = Field(max_length=50, description="Camera identifier")
    name: str = Field(max_length=100, description="Camera name/description")
    location: GeoLocation = Field(description="Camera location")
    address: str | None = Field(default=None, max_length=500, description="Camera address")
    camera_type: str | None = Field(
        default=None, max_length=50, description="Camera type (PTZ, fixed, etc.)"
    )
    owner: str | None = Field(default=None, max_length=100, description="Camera owner")
    status: CameraStatus = Field(default=CameraStatus.UNKNOWN, description="Camera status")
    stream_url: str | None = Field(default=None, max_length=500, description="Stream URL")
    is_public: bool = Field(default=False, description="Public camera flag")
    coverage_radius_meters: int | None = Field(
        default=None, ge=0, description="Coverage radius in meters"
    )
    notes: str | None = Field(default=None, max_length=1000, description="Additional notes")


class CameraCreate(CameraBase):
    """Schema for creating a Camera entity."""

    pass


class CameraResponse(CameraBase, TimestampMixin):
    """Schema for Camera entity response."""

    id: str = Field(description="Unique camera identifier")
    last_online: datetime | None = Field(default=None, description="Last online timestamp")


# License Plate Schemas


class LicensePlateBase(RTCCBaseModel):
    """Base schema for LicensePlate entity."""

    plate_number: str = Field(max_length=20, description="License plate number")
    plate_state: str = Field(max_length=2, description="License plate state")
    plate_type: str | None = Field(
        default=None, max_length=50, description="Plate type (standard, commercial, etc.)"
    )
    is_wanted: bool = Field(default=False, description="Wanted plate flag")
    alert_reason: str | None = Field(default=None, max_length=500, description="Reason for alert")


class LicensePlateCreate(LicensePlateBase):
    """Schema for creating a LicensePlate entity."""

    pass


class LicensePlateResponse(LicensePlateBase, TimestampMixin):
    """Schema for LicensePlate entity response."""

    id: str = Field(description="Unique license plate identifier")
    sighting_count: int = Field(default=0, description="Number of sightings")
    last_seen_at: datetime | None = Field(default=None, description="Last sighting timestamp")
    last_seen_location: GeoLocation | None = Field(default=None, description="Last seen location")


# Association Schemas


class AssociationBase(RTCCBaseModel):
    """Base schema for Association (relationship) between entities."""

    source_type: str = Field(description="Source entity type")
    source_id: str = Field(description="Source entity ID")
    target_type: str = Field(description="Target entity type")
    target_id: str = Field(description="Target entity ID")
    association_type: AssociationType = Field(description="Type of association")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score (0-1)")
    start_date: datetime | None = Field(default=None, description="Association start date")
    end_date: datetime | None = Field(default=None, description="Association end date")
    notes: str | None = Field(default=None, max_length=1000, description="Additional notes")


class AssociationCreate(AssociationBase):
    """Schema for creating an Association."""

    pass


class AssociationResponse(AssociationBase, TimestampMixin):
    """Schema for Association response."""

    id: str = Field(description="Unique association identifier")
    source_name: str | None = Field(default=None, description="Source entity display name")
    target_name: str | None = Field(default=None, description="Target entity display name")
